import os
import re

from submin.path.path import Path
from submin.common.osutils import mkdirs

class c_apacheconf():
	'''Commands to change apache config
Usage:
    apacheconf create all - create all apache config files

    Different files are created for each service (submin webui, svn, trac,
    etc.). The files will be created in '<submin env>/conf/apache-*.conf. Some
    examples are:
     - apache-webui-cgi.conf
     - apache-webui-wsgi.conf
     - apache-svn.conf
     - apache-trac-cgi.conf
     - (...)

    Now the files can be included in separate <VirtualHost> blocks. For each
    component, there can be multiple options, for example there is a CGI webui
    and a WSGI webui. Include only one of these: CGI is easiest, but slowest.
    For more performance, choose WSGI if available.

    Look inside the config files for more configuration instructions.'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.env = Path(sa.env)
		self.argv = argv

	def subcmd_create(self, argv):
		if len(argv) != 1 or argv[0] != 'all':
			self.sa.execute(['help', 'apacheconf'])
			return

		for key, value in self.defaults.iteritems():
			self.init_vars[key] = value

		self._apache_conf_create()

	def _apache_conf_create(self):
		from time import strftime
		from submin.template.shortcuts import evaluate

		self.init_vars['datetime_generated'] = strftime("%Y-%m-%d %H:%M:%S")

		if 'PYTHONPATH' in os.environ:
			self.init_vars['setenv_pythonpath'] = 'SetEnv PYTHONPATH %s' % os.environ['PYTHONPATH']
		else:
			self.init_vars['setenv_pythonpath'] = ''

		if self.init_vars['submin_base_url'] == "/":
			# Doesn't make sense to have an Alias if the base url is "/"
			self.init_vars['webui_origin'] = 'DocumentRoot "%(www_dir)s"' % self.init_vars
		else:
			# The alias is really picky about trailing slashes. Our experience
			# finds that no trailing slashes works best for both src and dst.
			# This is because without a trailing slash, the following will also
			# work as expected: http://localhost/submin
			submin_base_url = str(self.init_vars['submin_base_url']).rstrip('/')
			www_dir = str(self.init_vars['www_dir']).rstrip('/')
			self.init_vars['webui_origin'] = 'Alias "%s" "%s"' % (submin_base_url, www_dir)

		generate_configs = [
			'webui-cgi',
			'webui-wsgi',
			'svn',
			'trac-modpython',
			'trac-cgi',
			'trac-modwsgi',
			'trac-fcgid',
			'trac-no-anonymous'
		]
		generated = []
		basename = str(self.env + 'conf' + 'apache-%s.conf')
		template = 'subminadmin/apache-%s.conf'
		for name in generate_configs:
			fname = basename % name
			file(fname, 'w').write(evaluate(template % name, self.init_vars))
			generated.append(fname)

		basename = str(self.env + 'conf' + 'apache-2.4-%s.conf')
		self.init_vars['apache_2_4'] = True
		for name in generate_configs:
			fname = basename % name
			file(fname, 'w').write(evaluate(template % name, self.init_vars))
			generated.append(fname)

		print 'Apache files created:\n', '\n'.join(generated)

		print '''
   Please include ONE of the -webui- files and optionally -trac- and -svn-
   files (if you need/want that functionality). The -trac-no-anonymous.conf
   file can be used together with ONE other trac config file. The -2.4- files
   are for apache >= 2.4.

   Hint: cgi is simpler, but performs worse.

   Please read the instructions in the file for caveats and on how to include!
'''

	def urlpath(self, url):
		"""Strip scheme and hostname from url, leaving only the path. Also
		fix slashes (need leading, no trailing, no doubles)"""
		# remove schema + hostname
		url = re.sub('^[^:]*://[^/]+', '/', url)

		return self.canonicalize(url)

	def canonicalize(self, path):
		# strip trailing slash
		path = path.rstrip('/')
		# add leading slash
		if path == "" or path[0] != '/':
			path = '/' + path

		path = re.sub('/+', '/', path)

		return path

	def run(self):
		os.environ['SUBMIN_ENV'] = self.sa.env
		from submin.models import options

		if len(self.argv) < 1:
			self.sa.execute(['help', 'apacheconf'])
			return

		self.defaults = {
			'type': 'all',
		}
		cgi_bin_dir = os.path.join(self.sa.env, 'cgi-bin')
		self.init_vars = {
			'submin_env': self.canonicalize(self.sa.env),
			'www_dir': self.canonicalize(str(self.sa.basedir_www)),
			'cgi_bin_dir': self.canonicalize(str(cgi_bin_dir)),
			# Don't use options.url_path here, we need the url without
			# trailing slash.
			'submin_base_url': self.urlpath(options.value('base_url_submin')),
			'svn_base_url': self.urlpath(options.value('base_url_svn')),
			'trac_base_url': self.urlpath(options.value('base_url_trac')),
			'svn_dir': options.env_path('svn_dir'),
			'trac_dir': options.env_path('trac_dir'),
			'authz_file': options.env_path('svn_authz_file'),
		}
		self.auth_type = options.value('auth_type')

		# variables depending on auth type
		if self.auth_type == "sql":
			pass
		elif options.value('auth_type') == "htaccess":
			self.init_vars.update({
				'access file': options.value('auth_access_file'),
			})

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'apacheconf'])
			return

		subcmd(self.argv[1:])
