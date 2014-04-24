from submin.path.path import Path
from submin.template.shortcuts import evaluate
from submin.common.osutils import mkdirs
import os
import re
import errno

from common import www_user

class c_nginxconf():
	'''Commands to change NGINX config
Usage:
    nginxconf create all [<template>] - create all configs, save to multiple files
                                        using <template> filename

    With the 'all' method, separate files are created and the different sections
    (only submin webui for now) are created as different files as well. The
    template will be used to create each filename. For example, when using a
    template of '/var/lib/submin/conf/nginx.conf', the following files will
    be created in '/var/lib/submin/conf/':
     - nginx-webui-wsgi.conf

    By default <template> is '<submin env>/conf/nginx.conf'.

    Now the files can be included in separate server blocks.'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def subcmd_create(self, argv):
		from submin.models import options
		if len(argv) == 0:
			self.sa.execute(['help', 'nginxconf'])
			return

		if argv[0] != 'all':
			# the only option at the moment
			self.sa.execute(['help', 'nginxconf'])
			return
			
		if len(argv) > 1: # not always true with 'all'
			self.init_vars['output'] = argv[1]
		else: #  argv[0] must be 'all'
			self.init_vars['output'] = options.env_path() + 'conf' + 'nginx.conf'

		mkdirs(self.sa.env + '/run')

		self._nginx_conf_create()
		self.sa.execute(['unixperms', 'fix'])

	def _nginx_conf_create(self):
		from time import strftime

		template = str(self.init_vars['output'])
		if template.endswith('.conf'):
			template = template[:-len('.conf')]

		fname_submin_wsgi = template + '-webui-wsgi.conf'
		fname_uwsgi_ini = template + '-webui-uwsgi.ini'

		self.init_vars['submin_wsgi'] = fname_submin_wsgi
		self.init_vars['uwsgi_ini'] = fname_uwsgi_ini
		self.init_vars['datetime_generated'] = strftime("%Y-%m-%d %H:%M:%S")

		header_webui = evaluate('subminadmin/nginx-header.conf', self.init_vars)
		submin_wsgi = evaluate('subminadmin/nginx-webui-wsgi.conf', self.init_vars)
		uwsgi_ini = evaluate('subminadmin/uwsgi-webui.ini', self.init_vars)

		file(fname_submin_wsgi, 'w').write(header_webui + submin_wsgi)
		file(fname_uwsgi_ini, 'w').write(uwsgi_ini)
		print 'Nginx files created:\n', "\n".join([fname_submin_wsgi, fname_uwsgi_ini])

		print '''
   Please include the relevent .conf files in your NGINX config.'''

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
			self.sa.execute(['help', 'nginxconf'])
			return

		self.defaults = {
			'output': options.env_path() + 'conf' + 'nginx.conf'
		}
		user = www_user()
		self.init_vars = {
			'submin_env': self.canonicalize(str(self.sa.env)),
			'www_dir': self.canonicalize(str(self.sa.basedir_www)),
			# Don't use options.url_path here, we need the url without
			# trailing slash.
			'submin_base_url': self.urlpath(options.value('base_url_submin')),
			'www_uid': user.pw_uid,
			'www_gid': user.pw_gid,
		}
		self.init_vars['real_wsgi'] = os.path.realpath(
			os.path.join(self.init_vars['www_dir'], 'submin.wsgi'))

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'nginxconf'])
			return

		subcmd(self.argv[1:])
