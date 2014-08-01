import os
import sys
import codecs
import errno

from pwd import getpwnam

from submin.models import options
from submin.models import user

def run():
	env_path = options.env_path()
	filename = os.path.expanduser("~/.ssh/authorized_keys")
	filename = options.value("git_dev_authorized_keysfile", filename)
	if not os.path.exists(os.path.dirname(filename)):
		try:
			# create dir and file if one of them doesn't exist
			os.mkdir(os.path.dirname(filename))
			file(filename, 'a')
		except OSError, e:
			if e.errno != errno.EACCES:
				raise
			raise Exception('Could not write "%s", please check that git user can write it.' % filename)

		# Make the authorized_keys file only readable to the git-user
		gituser = options.value("git_user")
		owner = getpwnam(gituser)
		os.chown(os.path.dirname(filename), owner.pw_uid, owner.pw_gid)
		os.chmod(filename, 0o600)

	www_key_file = env_path + "conf" + "id_dsa.pub"
	if not www_key_file.exists():
		raise Exception("Could not find the submin ssh-key. Please run submin2-admin git init")
	key_fp = open(str(www_key_file))
	www_key = key_fp.readline().strip()
	key_fp.close()

	# instead of writing ascii, write utf-8 encoding
	fp = codecs.open(str(filename), "w+", 'utf-8')
	env_vars = "PATH='%s' PYTHONPATH='%s'" % \
			(options.value("env_path"), ':'.join(sys.path))
	fp.write('command="%s submin2-admin \'%s\' git admin" %s\n' % \
			(env_vars, env_path, www_key))
	userlist = user.list(user.FakeAdminUser())
	for x in userlist:
		u = user.User(x)
		ssh_keys = u.ssh_keys()
		if not ssh_keys:
			continue
		for ssh_key in ssh_keys:
			fp.write('command="%s submin2-admin \'%s\' git user %s" %s\n' % \
					(env_vars, env_path, u, ssh_key["key"]))
	fp.close()
