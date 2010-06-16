import os
import sys
import commands

ERROR_STR = "submin-admin git %s is not supposed to be called by users."

def die(cmd):
	print >>sys.stderr, ERROR_STR % cmd
	sys.exit(1)

class ProgramNotFoundError(Exception):
	def __init__(self, prog, path_searched):
		self.prog = prog
		self.path_searched = path_searched

def which(program):
	from submin.models import options

	def is_exe(fpath):
		return os.path.exists(fpath) and os.access(fpath, os.X_OK)

	env_path = options.value("env_path")
	for path in env_path.split(os.pathsep):
		prog_path = os.path.join(path, program)
		if is_exe(prog_path) and os.path.isfile(prog_path):
			return prog_path

	raise ProgramNotFoundError(program, env_path)

class CmdException(Exception):
	def __init__(self, usermsg, errormsg):
		self.usermsg = usermsg
		self.errormsg = errormsg
		Exception.__init__(self)

def executeCmd(cmd, usermsg=""):
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	if exitstatus != 0:
		raise CmdException(usermsg, outtext)

class c_git:
	"""Commands related to git-support
Usage:
	git init          - Initialises git support; creates a user and more.
	                    Execute this as root!"""
	# The following commands are not to be called by users, but are internal
	# git-commands to be used via ssh. They are therefore not mentioned in the
	# usage text above.
	# - submin-admin <env> git user <username>
	#           -- to be called when trying to receive or upload a pack via
	#              ssh. Typically located in the command="" in the
	#              authorized_keys
	# - submin-admin <env> git admin
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
			return

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'git'])
			return

		try:
			subcmd(self.argv[1:])
		except CmdException, e:
			print >>sys.stderr, e.usermsg
			print >>sys.stderr, "Error message of the command was:", e.errormsg
			return

	def subcmd_user(self, args):
		if len(args) < 1:
			die("user")
		from submin.subminadmin import git
		git.user.run(args[0])

	def subcmd_admin(self, args):
		if 'SSH_ORIGINAL_COMMAND' not in os.environ:
			die("admin")
		from submin.subminadmin import git
		cmd = os.environ['SSH_ORIGINAL_COMMAND']

		if cmd.startswith('create '):
			_, repo = cmd.split(' ', 1)
			repo = repo.strip()
			if not repo or ' ' in repo:
				die()
			git.create.run(repo)
		elif cmd == 'update-auth':
			git.update.run()
		else:
			die()

	def subcmd_init(self, args):
		from submin.models import options

		if os.getuid() != 0:
			print >>sys.stderr, "Please execute `git init' as root."
			return

		try:
			sudo_bin = which("sudo")
			git_bin  = which("git")
		except ProgramNotFoundError, e:
			print 'Could not find %s, which is required for git init.' % e.prog
			return

		from submin.subminadmin import c_unixperms
		apache = c_unixperms.c_unixperms(None, None).apache_user()
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
				print >>sys.stderr, "Aborting."
				return

		# Now add the www-user to the git-group and chgrp of essential files
		# (settings file, database and paths.)
		git_pw = getpwnam(git_user)
		self.add_user_to_group(apache.pw_name, git_pw.pw_gid)
		self.chgrp_relevant_files(git_uid=git_pw.pw_uid, git_gid=git_pw.pw_gid)

		# Set the git_user option to the git-user
		options.set_value("git_user", git_user)

		# Ask ssh-host (default localhost)
		ssh_host = self.prompt_user("What is the host-name of the ssh-server?",
				"localhost")
		options.set_value("git_ssh_host", ssh_host)

		# Ask ssh-port (default 22)
		ssh_port = self.prompt_user("On what port is the ssh-server available?",
				"22")
		options.set_value("git_ssh_port", ssh_port)

		# Install .ssh/authorized_keys
		# This is kind-of elaborate, since the update-auth command is re-used
		# here, which is intended to be called via ssh. Since that is obviously
		# not possible yet, fake setting the SSH_ORIGINAL_COMMAND by passing it
		# as an environment variable.
		cmd = "sudo -H -u %s SSH_ORIGINAL_COMMAND='update-auth' submin-admin '%s' git admin" % (git_user,
				options.env_path())
		executeCmd(cmd, "Could not install authorized_keys-file")

	def prompt_user(self, prompt, defval):
		a = raw_input("%s [%s]> " % (prompt, defval))

		if a == '':
			return defval

		return a

	def create_user(self, username, homedir):
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

	def chgrp_relevant_files(self, git_uid, git_gid):
		from submin.models import options

		# Fix permissions for paths, which the git-user needs to be able to
		# access, in order to also access files within
		os.chown(str(options.env_path()), -1, int(git_gid))
		os.chown(str(options.env_path() + "conf"), -1, int(git_gid))
		os.chown(str(options.env_path("git_dir")), int(git_uid),
				int(git_gid))

		# Now, fix the permissions for the actual files
		os.chown(str(options.env_path() + "conf" + "settings.py"), -1,
				int(git_gid))
		os.chown(str(options.env_path() + "conf" + "submin.db"), -1,
				int(git_gid))
