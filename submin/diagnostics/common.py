import os

from submin.models import options
from submin.common.execute import check_output
from subprocess import CalledProcessError

class ApacheCtlError(Exception):
	pass

def apache_modules():
	path = options.value('env_path', "/bin:/usr/bin:/usr/local/bin:/opt/local/bin")
	paths = path.split(':')
	paths.extend(['/sbin', '/usr/sbin'])
	path = ':'.join(paths)
	env_copy = os.environ.copy()
	env_copy['PATH'] = path
	modules = []
	cmds = [
		['apachectl', '-t', '-D', 'DUMP_MODULES'],
		['apache2ctl', '-t', '-D', 'DUMP_MODULES'],
		# Gentoo specific workaround (see #326)
		['apache2ctl', 'modules'],
	]

	for cmd in cmds:
		try:
			for line in check_output(cmd, env=env_copy).split('\n'):
				if line.endswith('(shared)') or line.endswith('(static)'):
					modules.append(line.strip().split(' ')[0])
		except OSError:
			continue # try the next command, if any
		except CalledProcessError, e:
			raise ApacheCtlError(e)
		else:
			return modules

	raise ApacheCtlError('Executable apachectl not found, tried: ' + (', '.join(["'" + ' '.join(x) + "'" for x in cmds])))
