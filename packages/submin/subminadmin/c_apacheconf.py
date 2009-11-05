from submin.path.path import Path
import os

class c_apacheconf():
	'''Commands to change apache config
Usage:
	apacheconf create               - create config interactively
	apacheconf create wsgi <output> - create wsgi config, save to <output>
	apacheconf create cgi <output>  - create cgi config, save to <output>'''

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
		if len(argv) == 0:
			try:
				self.interactive()
			except KeyboardInterrupt:
				print
			return

		if len(argv) > 1 and argv[0] == 'wsgi' or argv[0] == 'cgi':
			for key, value in self.defaults.iteritems():
				self.init_vars[key] = value

			self.init_vars['type'] = argv[0]
			self.init_vars['output'] = argv[1]

			self._apache_conf_create()
			return

		self.sa.execute(['help', 'apacheconf'])
		return

	def _apache_conf_create(self):
		from time import strftime
		self.init_vars['REQ_FILENAME'] = '%{REQUEST_FILENAME}'; # hack :)
		self.init_vars['datetime_generated'] = strftime("%Y-%m-%d %H:%M:%S")
		contents = '''# Generated on: %(datetime_generated)s
# This config file was automatically created with submin-admin. If you use
# this command again, it will overwrite all changes to this file. The
# recommanded way to regenerate this file is to change the config with
# submin-admin and run:
#
#   submin-admin %(submin env)s apacheconf create
# 
#
# To make this config active, you have to include it in your apache
# config. The recommended way is to include it in one of your virtual hosts:
#
# <Virtualhost *:80>
#     <other configuration>
#
#     Include <path to this file>
# </VirtualHost>
#
''' % self.init_vars

		if self.auth_type == "sql":
			contents += self._apache_conf_auth_sql_head(self.init_vars)

		if self.init_vars['type'] == 'cgi':
			contents += self._apache_conf_cgi(self.init_vars)
		elif self.init_vars['type'] == 'wsgi':
			contents += self._apache_conf_wsgi(self.init_vars)

		contents += self._apache_conf_svn(self.init_vars)
		contents += self._apache_conf_trac(self.init_vars)

		file(str(self.init_vars['output']), 'w').write(contents)

		print '''
Apache file created: %(output)s

   Please include this in your apache config. Also make sure that you have
   the appropriate modules installed and enabled. Depending on your choices,
   these may include: mod_dav_svn, mod_authz_svn, mod_wsgi and mod_python
''' % self.init_vars

	def _apache_conf_cgi(self, vars):
		apache_conf_cgi = '''
    <IfModule mod_cgi.c>
        Alias "%(submin base url)s" "%(www dir)s"
		ScriptAlias "/submin.cgi" "%(cgi-bin dir)s/submin.cgi"
		<Directory "%(cgi-bin dir)s">
            Order allow,deny
            Allow from all

            Options ExecCGI FollowSymLinks
            AddHandler cgi-script py cgi pl

            SetEnv SUBMIN_ENV %(submin env)s
		</Directory>
        <Directory "%(www dir)s">
            Order allow,deny
            Allow from all
            Options FollowSymLinks

            RewriteEngine on
            RewriteBase %(submin base url)s

            RewriteCond %(REQ_FILENAME)s !-f
            RewriteRule ^(.+)$ /submin.cgi/$1

            RewriteRule ^/?$ /submin.cgi/
        </Directory>
    </IfModule>
    <IfModule !mod_cgi.c>
        AliasMatch "^%(submin base url)s" %(www dir)s/nocgi.html
        <Location "%(submin base url)s">
            Order allow,deny
            Allow from all
        </Location>
    </IfModule>
''' % vars
		return apache_conf_cgi

	def _apache_conf_wsgi(self, vars):
		apache_conf_wsgi = '''
    <IfModule mod_wsgi.c>
        WSGIScriptAlias "%(submin base url)s" %(www dir)s/submin.wsgi
        AliasMatch ^%(submin base url)s/css/(.*) %(www dir)s/css/$1
        AliasMatch ^%(submin base url)s/img/(.*) %(www dir)s/img/$1
        AliasMatch ^%(submin base url)s/js/(.*) %(www dir)s/js/$1

        <Location "%(submin base url)s">
            Order allow,deny
            Allow from all
            SetEnv SUBMIN_ENV "%(submin env)s"
        </Location>
    </IfModule>
    <IfModule !mod_wsgi.c>
        AliasMatch "^%(submin base url)s" %(www dir)s/nowsgi.html
        <Location "%(submin base url)s">
            Order allow,deny
            Allow from all
        </Location>
    </IfModule>
''' % vars
		return apache_conf_wsgi

	def _apache_conf_svn(self, vars):
		if self.auth_type == "sql":
			auth_conf = self._apache_conf_auth_sql(vars)
		elif self.auth_type == "htaccess":
			auth_conf = self._apache_conf_auth_sql(vars)

		vars['apache_conf_auth'] = auth_conf

		apache_conf_svn = '''
    <IfModule mod_dav_svn.c>
        <Location %(svn base url)s>
            DAV svn
            SVNParentPath %(svn dir)s

            AuthType Basic
            AuthName "Subversion repository"

%(apache_conf_auth)s

            # Authorization
            AuthzSVNAccessFile %(authz file)s

            Satisfy Any
            Require valid-user
        </Location>
    </IfModule>
''' % vars
		return apache_conf_svn

	def _apache_conf_auth_sql_head(self, vars):
		conf = '''
    DBDriver sqlite3
    DBDParams "%(submin env)s/conf/submin.db"
''' % vars
		return conf

	def _apache_conf_auth_sql(self, vars):
		conf = '''
            # Authentication
            AuthBasicProvider dbd
            AuthDBDUserPWQuery "SELECT password FROM users WHERE name=%%s"
''' % vars
		return conf

	def _apache_conf_auth_htaccess(self, vars):
		conf = '''
            # Authentication
            AuthUserFile %(access file)s
''' % vars
		return conf

	def _apache_conf_trac(self, vars):
		if self.auth_type == "sql":
			auth_conf = self._apache_conf_auth_sql(vars)
		elif self.auth_type == "htaccess":
			auth_conf = self._apache_conf_auth_sql(vars)

		vars['apache_conf_auth'] = auth_conf

		apache_conf_trac = '''
    # Only load if mod_python is available
    <IfModule mod_python.c>
        <Location "%(trac base url)s">
           SetHandler mod_python
           PythonInterpreter main_interpreter
           PythonHandler trac.web.modpython_frontend
           PythonOption TracEnvParentDir "%(trac dir)s"
           PythonOption TracUriRoot "%(trac base url)s"
        </Location>

        <LocationMatch "%(trac base url)s/[^/]+/login">
           AuthType Basic
           AuthName "Trac"

%(apache_conf_auth)s

           Require valid-user
        </LocationMatch>
        AliasMatch "%(trac base url)s/[^/]+/chrome/site" %(trac dir)s/$1/htdocs
        <Directory %(trac dir)s/*/htdocs>
          Order allow,deny
          Allow from all
        </Directory>
    </IfModule>
    <IfModule !mod_python.c>
        AliasMatch "^%(trac base url)s" %(www dir)s/nomodpython.html
        <Location "%(trac base url)s">
            Order allow,deny
            Allow from all
        </Location>
    </IfModule>
''' % vars
		return apache_conf_trac

	def run(self):
		os.environ['SUBMIN_ENV'] = self.sa.env
		from submin.models.options import Options
		o = Options()

		if len(self.argv) < 1:
			self.sa.execute(['help', 'apacheconf'])
			return

		self.defaults = {
			'type': 'wsgi',
			'output': o.env_path() + 'conf' + 'apache.conf'
		}
		self.init_vars = {
			'submin env': self.sa.env,
			'www dir': self.sa.basedir_www,
			'cgi-bin dir': os.path.join(self.sa.env, 'cgi-bin'),
			'submin base url': o.value('base_url_submin'),
			'svn base url': o.value('base_url_svn'),
			'trac base url': o.value('base_url_trac'),
			'svn dir': o.env_path('svn_dir'),
			'trac dir': o.env_path('trac_dir'),
			'authz file': o.env_path('svn_authz_file'),
		}
		self.auth_type = o.value('auth_type')

		# variables depending on auth type
		if self.auth_type == "sql":
			pass
		elif o.value('auth_type') == "htaccess":
			self.init_vars.update({
				'access file': o.value('auth_access_file'),
			})

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'apacheconf'])
			return

		subcmd(self.argv[1:])
