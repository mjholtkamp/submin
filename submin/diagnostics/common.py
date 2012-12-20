import os
import subprocess

from submin.models import options

def apache_modules():
	path = options.value('env_path', "/bin:/usr/bin:/usr/local/bin:/opt/local/bin")
	paths = path.split(':')
	paths.extend(['/sbin', '/usr/sbin'])
	path = ':'.join(paths)
	env_copy = os.environ.copy()
	env_copy['PATH'] = path
	cmd = ['apachectl', '-t', '-D', 'DUMP_MODULES']
	modules = []
	for line in subprocess.check_output(cmd, env=env_copy).split('\n'):
		if line.endswith('(shared)') or line.endswith('(static)'):
			modules.append(line.strip().split(' ')[0])

	return modules
				
