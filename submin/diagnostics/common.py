import os
import urllib2
import re

from submin.models import options
from submin.common.execute import check_output
from subprocess import CalledProcessError, STDOUT

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
			output = check_output(cmd, stderr=STDOUT, env=env_copy)
		except OSError as e:
			errormsgs.append(str(e))
			continue # try the next command, if any
		except CalledProcessError as e:
			errormsgs.append(e.output)
			continue # try the next command, if any
		else:
			errormsgs.append('')

			for line in output.split('\n'):
				if line.endswith('(shared)') or line.endswith('(static)'):
					module = line.strip().split(' ')[0]
					modules.append(module.replace('_module', ''))

		if len(modules) > 0:
			return modules # return if any command doing the work

	# Above commands didn't work, maybe because we do not have permission to
	# view SSL certificate. This lets apache fail to verify and thus fail
	# to dump the list of modules (see #330).  Final try, direct via URL...
	cmds.append(['[internal URL get]', server_info_url])
	try:
		response = urllib2.urlopen(server_info_url)
	except urllib2.HTTPError as e:
		errormsgs.append('HTTP error %u' % (e.code, ))
	except urllib2.URLError as e:
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
		errormsg += " * command: '%s', errormsg:\n\n%s\n\n" % \
				(' '.join(cmd), msg)

	errormsg = errormsg.replace('<', '&lt;').replace('>', '&gt;')
	raise ApacheCtlError(errormsg)

def add_labels(results, all_key, warnings, fails):
	"""Will add labels to the results dict and return it.
	These labels can be used in the template to mark them as warning or
	failures.

	For each key in warnings and fails will check if the key exists in
	results. If the value is False, will add a label key + '_label' with
	the value 'warn' label for warnings and 'fail' for fails.

	The all_key will be set to 'warn' if there was at least one warning,
	or if there was at least one failure, it will be set to 'fail'."""

	all_label = 'ok'
	for key in warnings:
		if key in results:
			if results[key]:
				results[key + '_label'] = 'ok'
			else:
				results[key + '_label'] = 'warn'
				all_label = 'warn'

	for key in fails:
		if key in results:
			if results[key]:
				results[key + '_label'] = 'ok'
			else:
				results[key + '_label'] = 'fail'
				all_label = 'fail'

	results[all_key] = all_label == 'ok'
	results[all_key + '_label'] = all_label

	return results

