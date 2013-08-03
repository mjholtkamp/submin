import os

from submin.models import options
from submin.common.execute import check_output

class ApacheCtlNotFound(Exception):
	pass

def apache_modules():
	path = options.value('env_path', "/bin:/usr/bin:/usr/local/bin:/opt/local/bin")
	paths = path.split(':')
	paths.extend(['/sbin', '/usr/sbin'])
	path = ':'.join(paths)
	env_copy = os.environ.copy()
	env_copy['PATH'] = path
	modules = []
	apachectl_names = ['apachectl', 'apache2ctl']

	for apachectl in apachectl_names:
		cmd = [apachectl, '-t', '-D', 'DUMP_MODULES']
		try:
			for line in check_output(cmd, env=env_copy).split('\n'):
				if line.endswith('(shared)') or line.endswith('(static)'):
					modules.append(line.strip().split(' ')[0])
		except OSError:
			continue # try the next executable
		else:
			return modules

	raise ApacheCtlNotFound('Tried: ' + ', '.join(apachectl_names))
