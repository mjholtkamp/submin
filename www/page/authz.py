from lib.utils import mimport
iif = mimport('lib.utils').iif
html = mimport('lib.html')
mod_authz = mimport('lib.authz')

def handler(input):
	SubmergeEnv = input.req.get_options()['SubmergeEnv']

	import ConfigParser
	cp = ConfigParser.ConfigParser()
	cp.read(SubmergeEnv)
	try:
		authz_file = cp.get('svn', 'authz_file')
	except ConfigParser.NoSectionError, e:
		print e, 'in', SubmergeEnv
		return

	authz = mod_authz.Authz(authz_file)

	print html.header('Permissions')
	print '<h2>Permissions</h2>'
	print '<table>'
	print '\t<thead>'
	print '\t\t<th style="width: 150px" align="left">user / group</th>'
	print '\t\t<th align="left">Permission</th>'
	print '\t</thead>'

	paths = authz.paths()
	paths.sort()
	for repos, path in paths:
		print '\t<tr>'
		print '\t\t<th colspan="2" align="left" ' +\
			'style="border-top: 1px solid #000">%s - %s</th>' % \
			(iif(repos, repos, ''), path)
		print '\t</tr>'
		permissions = authz.permissions(repos, path)
		permissions.sort()
		for user, permission in permissions:
			print '\t<tr>'
			print '\t\t<td>%s</td>' % user
			print '\t\t<td>%s</td>' % iif(permission, permission, '-')
			print '\t</tr>'
	print '</table>'

	print html.footer()
