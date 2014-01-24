import os
import sys
import stat
from common import executeCmd, which, CmdException, SubminAdminCmdException, www_user
from submin.common.osutils import mkdirs

ERROR_STR = "submin2-admin git %s is not supposed to be called by users."

def die(cmd):
	print >>sys.stderr, ERROR_STR % cmd
	sys.exit(1)

class ProgramNotFoundError(Exception):
	def __init__(self, prog, path_searched):
		self.prog = prog
		self.path_searched = path_searched

class c_git:
	"""Commands related to git-support
Usage:
    git init                 - Initialises git support; creates a user and more.
                               Execute this as root!
    git fix_perms            - Fixes unix permissions. Execute as root!
    git hook update [<repo>] - Rewrite the git hooks for <repo>. This includes
                               the 'update' hooks, but also the 'post-receive'
                               hooks. If no repository is given, all (git)
                               repositories are updated. Execute as root!"""
	# The following commands are not to be called by users, but are internal
	# git-commands to be used via ssh. They are therefore not mentioned in the
	# usage text above.
	# - submin2-admin <env> git user <username>
	#           -- to be called when trying to receive or upload a pack via
	#              ssh. Typically located in the command="" in the
	#              authorized_keys
	# - submin2-admin <env> git admin
	#           -- to be called via ssh by the web interface to create a
	#              repository with the correct git-user permissions. The
	#              SSH_ORIGINAL_COMMAND can have two commands:
	#              - create <repo>
	#              - update-auth

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def run(self):
		if len(self.argv) < 1:
			self.sa.execute(['help', 'git'])
			return False

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'git'])
			return False

		try:
			subcmd(self.argv[1:])
		except SubminAdminCmdException:
			pass
		except CmdException, e:
			print >>sys.stderr, e.usermsg
			print >>sys.stderr, "Command:", e.cmd
			print >>sys.stderr, "Error message of the command was:", e.errormsg
			sys.exit(1)
		# other exceptions are just raised

		return True

	def subcmd_user(self, args):
		if len(args) < 1:
			die("user")
		from submin.subminadmin import git
		git.user.run(unicode(args[0], 'utf-8'))

	def subcmd_admin(self, args):
		if 'SSH_ORIGINAL_COMMAND' not in os.environ:
			die("admin")
		from submin.subminadmin import git
		cmd = os.environ['SSH_ORIGINAL_COMMAND']

		if cmd.startswith('create '):
			_, repo = cmd.split(' ', 1)
			repo = repo.strip()
			if not repo or ' ' in repo:
				die("create")
			git.create.run(repo)
		elif cmd.startswith('remove '):
			_, repo = cmd.split(' ', 1)
			repo = repo.strip()
			if not repo or ' ' in repo:
				die("remove")
			git.remove.run(repo)
		elif cmd == 'update-auth':
			git.update.run()
		elif cmd.startswith('update-notifications'):
			cmd_args = cmd.split(' ', 1)
			reposname = None
			if len(cmd_args) > 1 and cmd_args[1] != "":
				reposname = cmd_args[1]

			git.update_notifications.run(reposname)
		elif cmd.startswith('commit-email-hook '):
			cmd_args = cmd.split(' ', 2)
			if len(cmd_args) != 3:
				die('commit-email-hook')

			enable, repo = cmd_args[1:]
			repo = repo.strip()
			git.post_receive_hook.setCommitEmailHook(repo, enable == 'enable')
		elif cmd.startswith('trac-sync-hook '):
			cmd_args = cmd.split(' ', 2)
			if len(cmd_args) != 3:
				die('trac-sync-hook')

			enable, repo = cmd_args[1:]
			repo = repo.strip()
			git.post_receive_hook.setTracSyncHook(repo, enable == 'enable')
		else:
			die("admin")

	def subcmd_init(self, args):
		from submin.models import options

		if os.getuid() != 0:
			raise SubminAdminCmdException("Please execute `git init' as root.")

		try:
			sudo_bin = which("sudo")
			git_bin  = which("git")
		except ProgramNotFoundError, e:
			raise SubminAdminCmdException('Could not find %s, which is required for git init.' % e.prog)

		from submin.subminadmin import c_unixperms
		apache = www_user()
		self.create_ssh_key(owner=apache)

		# Ask the name of the git user, if it exists ask to use it or bail
		git_user = self.prompt_user("What user should the git-users connect as?",
				"git")

		from pwd import getpwnam
		# Create git user if it doesn't exist yet.
		try:
			pwd = getpwnam(git_user)
		except KeyError, e:
			self.create_user(git_user, options.env_path("git_dir"))
		else:
			use_it = self.prompt_user("User %s already exists. Use it?" % \
					git_user, "Yn")
			if use_it.lower() not in ("y", "yes", "yn"):
				raise SubminAdminCmdException('Aborting')

		# Now add the www-user to the git-group and chgrp of essential files
		# (settings file, database and paths.)
		git_pw = getpwnam(git_user)
		# XXX this is problably not necessary anymore
		self.add_user_to_group(apache.pw_name, git_pw.pw_gid)
		self.chgrp_relevant_files(git_uid=git_pw.pw_uid, git_gid=git_pw.pw_gid)

		# Set the git_user option to the git-user
		options.set_value("git_user", git_user)

		# Ask public ssh-host
		ssh_host = self.prompt_user("What is the public host-name of the ssh-server?",
				"localhost")
		options.set_value("git_ssh_host", ssh_host)

		# Ask internal ssh-host
		internal_ssh_host = self.prompt_user("What is the internal host-name of the ssh-server\n(used to, e.g., create repositories over fast local network)?",
				ssh_host)
		options.set_value("git_ssh_host_internal", internal_ssh_host)

		# Ask ssh-port (default 22)
		ssh_port = self.prompt_user("On what port is the ssh-server available?",
				"22")
		options.set_value("git_ssh_port", ssh_port)

		# Enable git as a vcs plugin
		vcs_plugins = options.value("vcs_plugins")
		if 'git' not in vcs_plugins.split(','):
			options.set_value("vcs_plugins", "%s,git" % vcs_plugins)

		# Install .ssh/authorized_keys
		# This is kind-of elaborate, since the update-auth command is re-used
		# here, which is intended to be called via ssh. Since that is obviously
		# not possible yet, fake setting the SSH_ORIGINAL_COMMAND by passing it
		# as an environment variable.
		cmd = "sudo -H -u %s SSH_ORIGINAL_COMMAND='update-auth' submin2-admin '%s' git admin" % (git_user,
				options.env_path())
		executeCmd(cmd, "Could not install authorized_keys-file. Please check whether the git-user has read-access to the submin-environment directory")

	def prompt_user(self, prompt, defval):
		a = raw_input("%s [%s]> " % (prompt, defval))

		if a == '':
			return defval

		return a

	def create_user_adduser(self, username, homedir):
		cmd = ["adduser",
			   "--system",
			   "--shell /bin/sh",
			   "--gecos 'git version control'",
			   "--group",
			   "--disabled-password",
			   "--home %s" % homedir,
			   "%s" % username
			  ]
		cmd = ' '.join(cmd)
		executeCmd(cmd, "Could not create user %s" % username)

	def create_user_useradd(self, username, homedir):
		cmd = ["useradd",
			   "--system",
			   "--shell /bin/sh",
			   "--comment 'git version control'",
			   "--user-group",
			   "--home %s" % homedir,
			   "%s" % username
			  ]
		cmd = ' '.join(cmd)
		executeCmd(cmd, "Could not create user %s" % username)

	def create_user(self, username, homedir):
		try:
			self.create_user_adduser(username, homedir)
		except CmdException, e:
			self.create_user_useradd(username, homedir)
			# if this fails, it will raise another CmdException,
			# which is not caught.

	def create_ssh_key(self, owner):
		from submin.models import options

		ssh_key_file = options.env_path() + 'conf' + 'id_dsa'
		ssh_pub_key = str(ssh_key_file) + '.pub'
		if ssh_key_file.exists():
			print >>sys.stderr, "Not creating ssh key, since one already exists:", ssh_key_file
			return
		cmd = 'ssh-keygen -t dsa -f %s -N ""' % ssh_key_file
		executeCmd(cmd, "Could not create an ssh key")

		# Fix permissions for the ssh-key
		os.chown(str(ssh_key_file), owner.pw_uid, owner.pw_gid)
		os.chmod(str(ssh_key_file), 0600)
		os.chown(ssh_pub_key, owner.pw_uid, owner.pw_gid)
		os.chmod(ssh_pub_key, 0644)
		print "ssh-key is now owned by %s" % owner.pw_name

	def add_user_to_group(self, username, group_id):
		cmd = "usermod -a -G %s %s" % (group_id, username)
		executeCmd(cmd, "Could not add %s to the git-group" % username)

	def subcmd_fix_perms(self, args):
		from submin.models import options
		from pwd import getpwnam
		git_user = options.value("git_user")
		git_pw = getpwnam(git_user)
		self.chgrp_relevant_files(git_uid=git_pw.pw_uid, git_gid=git_pw.pw_gid)

	def subcmd_hook(self, args):
		if len(args) < 1 or args[0] != 'update':
			self.sa.execute(['help', 'git'])
			return

		from submin.subminadmin import git
		reponame = None
		if len(args) > 1:
			reponame = unicode(args[1], 'utf-8')
		git.create.rewrite_hook(reponame)
		git.update_notifications.run(reponame)
		git.post_receive_hook.rewrite_hook(reponame)
		
		# fix permissions because we ran this as root
		self.sa.execute(['unixperms', 'fix'])

	def chgrp_relevant_files(self, git_uid, git_gid):
		from submin.models import options

		# Fix permissions for paths, which the git-user needs to be able to
		# access, in order to also access files within
		os.chown(str(options.env_path()), -1, int(git_gid))
		os.chmod(str(options.env_path()), 0750)
		conf_dir = options.env_path() + "conf"
		os.chown(str(conf_dir), -1, int(git_gid))

		# now make everything in git's home-dir owned by the git user and apache group
		from submin.subminadmin import c_unixperms
		apache = www_user()
		git_dir = options.env_path("git_dir")
		ssh_dir = git_dir + ".ssh"

		# make ssh dir, if not already exists
		mkdirs(ssh_dir)

		for root, dirs, files in os.walk(git_dir):
			for f in files:
				path = os.path.join(root, f)
				if root == ssh_dir:
					os.chown(path, int(git_uid), int(git_gid))
					os.chmod(path, 0700)
				else:
					# in Python 3.3, we can use follow_symlinks=False, instead
					# of this more complex way
					statinfo = os.lstat(path)
					if not stat.S_ISLNK(statinfo.st_mode):
						os.chown(path, int(git_uid), int(apache.pw_gid))
						os.chmod(path, 0750)
			for d in dirs:
				path = os.path.join(root, d)
				os.chown(path, int(git_uid), int(apache.pw_gid))
				os.chmod(path, 0750)

		# The git-directory itself should also be available to the apache-user,
		# So it can list the repositories
		os.chown(git_dir, int(git_uid), int(apache.pw_gid))

		# The ssh-directory can be really strict, only allow git
		os.chmod(ssh_dir, 0700)
		os.chown(ssh_dir, int(git_uid), int(git_gid))

		# Now, fix the permissions for the actual files
		os.chown(str(conf_dir + "settings.py"), -1, int(git_gid))
		os.chown(str(conf_dir + "submin.db"), -1, int(git_gid))

		# These last ones are a bit tricky, id_dsa and id_dsa.pub are
		# NOT owned by the git user, as they are client files owned
		# by the www user. However, SSH requires strict permissions
		# and id_dsa.pub needs to be readable by the git user, so it
		# can add the public key to the authorized_keys file.
		os.chown(str(conf_dir + "id_dsa.pub"), -1, int(git_gid))
		os.chmod(str(conf_dir + "id_dsa"), 0600)
