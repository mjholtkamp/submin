import os
import re

from submin.path.path import Path
from submin.template.shortcuts import evaluate
from submin.common.osutils import mkdirs

class c_apacheconf():
	'''Commands to change apache config
Usage:
    apacheconf create all [<template>] - create cgi config, save to multiple
                                         files using <template>

    Different files are created for each service (submin webui, svn, trac,
    etc.). The template will be used to create each filename. For example:
    if the template is '/var/lib/submin/conf/XYZ.conf', the following files
    will be created in '/var/lib/submin/conf/':
     - XYZ-webui-cgi.conf
     - XYZ-webui-wsgi.conf
     - XYZ-svn.conf
     - XYZ-trac-cgi.conf
     - (...)

    By default <template> is '<submin env>/conf/apache.conf'.

    Now the files can be included in separate <VirtualHost> blocks. For each
    component, there can be multiple options, for example there is a CGI webui
    and a WSGI webui. Include only one of these: CGI is easiest, but slowest.
    For more performance, choose WSGI if available'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def _get_value_from_user(self, prompt, default):
		defval = self.defaults[default]
		a = raw_input("%s [%s]> " % (prompt, defval))

		if a == '':
			self.init_vars[default] = defval
			return

		p = Path(a)
		if type(p) == type(defval):
			self.init_vars[default] = p
			return

		self.init_vars[default] = a

	def interactive(self):
		print '''
Choosing CGI or WSGI is a trade-off between speed and compatibility. CGI is
enabled for most Apache installations, but slower than WSGI. If you have WSGI
enabled (mod_wsgi), you should choose WSGI.
'''
		self._get_value_from_user("wsgi or cgi?", 'type')

		print '''
The Apache config file will be created, all we need now is a filename. THIS
FILE WILL BE OVERWRITTEN WITHOUT ANY WARNING! The default option is good in
most installations. Just include this file in your main apache config. The
recommended way is to include it in a VirtualHost.
'''
		self._get_value_from_user("Output file? (will be overwritten!!)",
			'output')

		self._apache_conf_create()

	def subcmd_create(self, argv):
		from submin.models import options
		if len(argv) == 0:
			try:
				self.interactive()
			except KeyboardInterrupt:
				print
			return

		minargs = -1 # invalid command
		if argv[0] in ('all'):
			minargs = 1

		if minargs > -1 and len(argv) >= minargs:
			for key, value in self.defaults.iteritems():
				self.init_vars[key] = value

			self.init_vars['type'] = argv[0]
			if len(argv) > 1: # not always true with 'all'
				self.init_vars['output'] = argv[1]
			else: #  argv[0] must be 'all'
				self.init_vars['output'] = options.env_path() + 'conf' + 'apache.conf'

			self._apache_conf_create()
			return

		self.sa.execute(['help', 'apacheconf'])
		return

	def _apache_conf_create(self):
		from time import strftime
		self.init_vars['datetime_generated'] = strftime("%Y-%m-%d %H:%M:%S")

		if os.environ.has_key('PYTHONPATH'):
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

		submin_cgi = evaluate('subminadmin/apache-webui-cgi-wrapper.conf', self.init_vars)
		submin_wsgi = evaluate('subminadmin/apache-webui-wsgi.conf', self.init_vars)
		submin_svn = evaluate('subminadmin/apache-svn.conf', self.init_vars)
		submin_trac_modpy = evaluate('subminadmin/apache-trac-modpython.conf', self.init_vars)
		submin_trac_cgi = evaluate('subminadmin/apache-trac-cgi-wrapper.conf', self.init_vars)
		submin_trac_modwsgi = evaluate('subminadmin/apache-trac-modwsgi.conf', self.init_vars)
		submin_trac_fcgid = evaluate('subminadmin/apache-trac-fcgid.conf', self.init_vars)
		submin_trac_no_anon = evaluate('subminadmin/trac-no-anonymous.conf', self.init_vars)

		template = str(self.init_vars['output'])
		if template.endswith('.conf'):
			template = template[:-len('.conf')]

		fname_submin_cgi = template + '-webui-cgi.conf'
		fname_submin_wsgi = template + '-webui-wsgi.conf'
		fname_svn = template + '-svn.conf'
		fname_trac_modpy = template + '-trac-modpython.conf'
		fname_trac_cgi = template + '-trac-cgi.conf'
		fname_trac_fcgid = template + '-trac-fcgid.conf'
		fname_trac_modwsgi = template + '-trac-modwsgi.conf'
		fname_trac_no_anon = template + '-trac-no-anonymous.conf'
		file(fname_submin_cgi, 'w').write(submin_cgi)
		file(fname_submin_wsgi, 'w').write(submin_wsgi)
		file(fname_svn, 'w').write(submin_svn)
		file(fname_trac_modpy, 'w').write(submin_trac_modpy)
		file(fname_trac_cgi, 'w').write(submin_trac_cgi)
		file(fname_trac_fcgid, 'w').write(submin_trac_fcgid)
		file(fname_trac_modwsgi, 'w').write(submin_trac_modwsgi)
		file(fname_trac_no_anon, 'w').write(submin_trac_no_anon)
		print 'Apache files created:\n', "\n".join([fname_submin_cgi,
			fname_submin_wsgi, fname_svn, fname_trac_modpy,
			fname_trac_cgi, fname_trac_fcgid, fname_trac_modwsgi,
			fname_trac_no_anon])

		print '''
   Please include the relevent files in your apache config. Do NOT include all
   files, but only select one version (e.g include svn and webui-cgi but not
    webui-wsgi).

   Also make sure that you have the appropriate modules installed and enabled.
   Depending on your choices, these may include: mod_dav_svn, mod_authz_svn,
   mod_authn_dbd, mod_dbd, mod_wsgi, mod_cgi, mod_cgid and mod_python'''

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
			'type': 'wsgi',
			'output': options.env_path() + 'conf' + 'apache.conf'
		}
		cgi_bin_dir = os.path.join(self.sa.env, 'cgi-bin')
		self.init_vars = {
			'submin_env': self.canonicalize(str(self.sa.env)),
			'www_dir': self.canonicalize(str(self.sa.basedir_www)),
			'cgi_bin_dir': self.canonicalize(str(cgi_bin_dir)),
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
