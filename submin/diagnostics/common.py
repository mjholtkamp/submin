import os
import urllib2
import re

from submin.models import options
from submin.common.execute import check_output
from subprocess import CalledProcessError

class ApacheCtlError(Exception):
	pass

def apache_modules():
	path = options.value('env_path',
			'/bin:/usr/bin:/usr/local/bin:/opt/local/bin')
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
	errormsgs = []
	server_info_url = options.value('apache_server_info_url',
		'http://localhost/server-info?list')

	for cmd in cmds:
		try:
			for line in check_output(cmd, env=env_copy).split('\n'):
				if line.endswith('(shared)') or line.endswith('(static)'):
					module = line.strip().split(' ')[0]
					modules.append(module.replace('_module', ''))
		except OSError, e:
			errormsgs.append(str(e))
			continue # try the next command, if any
		except CalledProcessError, e:
			errormsgs.append(str(e))
			continue # try the next command, if any
		else:
			errormsgs.append('')

		if len(modules) > 0:
			return modules # return if any command doing the work

	# Above commands didn't work, maybe because we do not have permission to
	# view SSL certificate. This lets apache fail to verify and thus fail
	# to dump the list of modules (see #330).  Final try, direct via URL...
	cmds.append(['[internal URL get]', server_info_url])
	try:
		response = urllib2.urlopen(server_info_url)
	except urllib2.HTTPError, e:
		errormsgs.append('HTTP error %u: %s' % (e.code, e.read()))
	except urllib2.URLError, e:
		errormsgs.append('URL error %u: %s' % (e.reason[0], e.reason[1]))
	else:
		html = response.read()
		modules = re.findall('<dd>mod_([^<]+)\.c</dd>', html)
		if len(modules) > 0:
			return modules
		errormsgs.append('Could not find list of modules at URL %s' %
				(server_info_url, ))

	# That failed too, give up and show our attempts
	errormsg = 'executable apachectl not found, tried:\n'
	for cmd, msg in zip(cmds, errormsgs):
		errormsg += "'" + ' '.join(cmd) + "', errormsg: " + msg + '\n'

	raise ApacheCtlError(errormsg)
