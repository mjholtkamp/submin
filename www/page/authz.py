import urllib
from lib.utils import mimport
iif = mimport('lib.utils').iif
html = mimport('lib.html')
exceptions = mimport('lib.exceptions')
mod_authz = mimport('lib.authz')

def _getauthz(input):
	SubmergeEnv = input.req.get_options()['SubmergeEnv']

	import ConfigParser
	cp = ConfigParser.ConfigParser()
	cp.read(SubmergeEnv)
	try:
		authz_file = cp.get('svn', 'authz_file')
	except ConfigParser.NoSectionError, e:
		raise Exception, str(e) + 'in' + str(SubmergeEnv)

	return mod_authz.Authz(authz_file)

def _base(input):
	req = input.req
	filename = req.uri
	if req.path_info:
		index = req.uri.rindex(req.path_info)
		filename = filename[:index]
	return filename

def _select(user, permission):
	checked = ' selected="selected"'
	select = '<select name="%s">' % user
	select += '\n\t\t\t<option value="-"%s>-</option>' % iif(permission == '', checked, '')
	select += '\n\t\t\t<option value="r"%s>r</option>' % iif(permission == 'r', checked, '')
	select += '\n\t\t\t<option value="rw"%s>rw</option>' % iif(permission == 'rw', checked, '')
	select += '\n\t\t</select>'
	return select

def handler(input):
	msg = None
	if input.get.has_key('msg'):
		msg = input.get['msg'][-1]

	authz = _getauthz(input)

	print html.header('Permissions')
	if msg:
		print '<p class="msg">%s</p>' % msg
	print '''<h2>Groups</h2>
<table>
	<thead>
		<td></td>
		<th style="width: 150px" align="left">Group</th>
		<th align="left">Members</th>
	</thead>
	<form action="%s/authz/delgroups" method="post" onsubmit="return confirm('Do you really want to delete these groups? (there is no undo!)')">
''' % _base(input)
	groups = authz.groups()
	groups.sort()
	for group in groups:
		members = authz.members(group)
		members.sort()
		print '''\t<tr>
		<td><input type="checkbox" name="%s" value="1" /></td>
		<td><a href="%s/group?group=%s">%s</a></td>
		<td>%s</td>
	</tr>''' % \
		(group, _base(input), urllib.quote(group), group, 
		', '.join(members))

	print '''
	<tr>
		<td colspan="3" align="right">
			<input type="submit" value="Delete checked groups" />
		</td>
	</tr>
	</form>
</table>'''

	print '<h2>Permissions</h2>'
	print '<table>'
	print '\t<thead>'
	print '\t\t<th style="width: 150px" align="left">user / group</th>'
	print '\t\t<th align="left">Permission</th>'
	print '\t</thead>'

	paths = authz.paths()
	paths.sort()
	for repos, path in paths:
		print '<form action="%s/authz/save" method="post">' % _base(input)
		print '\t<input type="hidden" name="path" value="%s%s" />' % \
				(iif(repos is not None, str(repos) + ':', ''), 
				urllib.quote(path))
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
			print '\t\t<td>%s</td>' % _select(user, permission)
			print '\t</tr>'
		print '\t<tr>'
		print '\t\t<td colspan="2" align="right">'
		print '\t\t\t<input type="submit" value="Save %s%s" />' %\
				(iif(repos is not None, str(repos) + ':', ''), path)
		print '\t\t</td>\n\t</tr>'
		print '</form>'
	print '</table>'

	print html.footer()

def save(input):
	authz = _getauthz(input)
	repos = None
	path = input.post['path']
	if ':' in path:
		repos, path = path.split(':', 1)
	for key, value in input.post.iteritems():
		if key != 'path':
			if value not in ('-', 'r', 'rw'):
				print 'Wrong permission:', value
				return
			if value == '-':
				value = ' '
			authz.setPermission(repos, path, key, value)

	raise exceptions.Redirect, '%s/authz' % _base(input)

def delgroups(input):
	authz = _getauthz(input)
	for group in input.post:
		try:
			authz.removeGroup(group)
		except mod_authz.UnknownGroupError:
			pass

	raise exceptions.Redirect, '%s/authz?msg=Groups+deleted' % _base(input)
