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
		<td style="width: 20px"></td>
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
		<td><a href="%s/authz/group?group=%s">%s</a></td>
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
</table>
<h3>Add a group</h3>
<table>
	<form action="%s/authz/addgroup" method="post">
	<tr>
		<td style="width: 20px"></td>
		<td style="width: 150px">New group</td>
		<td><input type="text" name="newgroup" /></td>
	</tr>
	<tr>
		<td colspan="3" align="right">
			<input type="submit" value="Add group" />
		</td>
	</tr>
	</form>
</table>''' % _base(input)

	print '<h2>Permissions</h2>'
	print '<p><a href="%s/authz/addpath">Add path</a></p>' % _base(input)

	print '<table style="border-collapse: collapse">'
	print '\t<thead>'
	print '\t\t<td></td>'
	print '\t\t<th style="width: 150px" align="left">user / group</th>'
	print '\t\t<th align="left">Permission</th>'
	print '\t</thead>'

	paths = authz.paths()
	paths.sort()
	for repos, path in paths:
		rpath = '%s%s' % (iif(repos, str(repos) + ':', ''), path)

		print '<form action="%s/authz/saveperm" method="post">' % _base(input)
		print '\t<input type="hidden" name="path" value="%s%s" />' % \
				(iif(repos is not None, str(repos) + ':', ''), 
				urllib.quote(path))
		print '\t<tr style="border-top: 1px solid #000">'
		print '\t\t<td></td>'
		print '\t\t<th align="left">%s%s</th>' % \
			(iif(repos, str(repos) + ':', ''), path)
		print '''\t\t<td>
		<a href="%s/authz/delpath?path=%s" onclick="return confirm('Do you really want to delete %s? (There is no undo)')" title="Delete">[X]</a>
		| <a href="%s/authz/addperm?path=%s" title="Add permission">[+]</a>
		</td>''' % \
				(_base(input), urllib.quote(rpath), rpath, _base(input), 
				urllib.quote(rpath))
		print '\t</tr>'
		permissions = authz.permissions(repos, path)
		permissions.sort()
		for user, permission in permissions:
			print '\t<tr>'
			print '\t\t<td><input type="checkbox" title="Delete this user from %s" name="del_%s" value="1" /></td>' % (rpath, user)
			print '\t\t<td>%s</td>' % user
			print '\t\t<td>%s</td>' % _select(user, permission)
			print '\t</tr>'
		print '\t<tr>'
		print '\t\t<td></td>'
		print '\t\t<td colspan="2" align="right">'
		print '\t\t\t<input type="submit" value="Save %s%s" />' %\
				(iif(repos is not None, str(repos) + ':', ''), path)
		print '\t\t</td>\n\t</tr>'
		print '</form>'
	print '</table>'

	print html.footer()

def saveperm(input):
	authz = _getauthz(input)
	repos = None
	path = input.post['path']
	if ':' in path:
		repos, path = path.split(':', 1)
	for key, value in input.post.iteritems():
		if key != 'path' and not key.startswith('del'):
			if value not in ('-', 'r', 'rw'):
				print 'Wrong permission:', value
				return
			if value == '-':
				value = ' '
			authz.setPermission(repos, path, key, value)
		elif key.startswith('del'):
			member = key
			authz.removePermission(repos, path, member[4:])

	raise exceptions.Redirect, '%s/authz?msg=Permissions+saved' % _base(input)

def addperm(input):
	authz = _getauthz(input)
	if input.get.has_key('path'):
		path = input.get['path'][-1]
		print html.header('Adding permission to %s' % path)
		print '<h2>Adding permission to %s</h2>' % path
		print '<p>Back to <a href="%s/authz">Authz management</a></p>' % _base(input)
		print '''<form action="%s/authz/addperm" method="post" name="perm">
	<input type="hidden" name="path" value="%s" />
	<input type="text" name="member" /> %s <input type="submit" value="Add user" />
</form>''' % (_base(input), path, _select('newuser', '-'))

		print '<h2>Groups <small>(For your adding convenience)</small>:</h2><ul>'
		groups = authz.groups()
		groups.sort()
		for group in groups:
			print '''
		<li><a href="#" onclick="document.perm.member.value='@%s'; return false">%s</a></li>''' %\
				(group, group)
		print '</ul>'

		print html.footer()
	elif input.post.has_key('member'):
		repos = None
		path = input.post['path']
		if ':' in path:
			repos, path = path.split(':', 1)

		member = input.post['member']
		permission = input.post['newuser']
		if permission not in ('-', 'r', 'rw'):
			print 'Wrong permission:', value
			return
		if permission == '-':
			permission = ' '
		authz.setPermission(repos, path, member, permission)
		raise exceptions.Redirect, '%s/authz?msg=Permissions+added' % _base(input)

def delpath(input):
	authz = _getauthz(input)
	if input.get.has_key('path'):
		repos = None
		path = input.get['path'][-1]
		if ':' in path:
			repos, path = path.split(':', 1)
		authz.removePath(repos, path)
	raise exceptions.Redirect, '%s/authz?msg=Path+deleted' % _base(input)

def addpath(input):
	authz = _getauthz(input)
	if not input.post.has_key('path'):
		print html.header('Adding path')
		print '<h2>Adding path</h2>'
		print '<p>Back to <a href="%s/authz">Authz management</a></p>' % _base(input)
		print 'Something with browsing the svn-tree :)'
		print html.footer()
	elif input.post.has_key('path'):
		# something with authz.addPath(repos, path)
		raise exceptions.Redirect, '%s/authz?msg=Path+adding+not+implemented' % _base(input)


def delgroups(input):
	authz = _getauthz(input)
	for group in input.post:
		try:
			authz.removeGroup(group)
		except mod_authz.UnknownGroupError:
			pass

	raise exceptions.Redirect, '%s/authz?msg=Groups+deleted' % _base(input)

def group(input):
	authz = _getauthz(input)
	group = input.get['group'][-1]
	members = authz.members(group)
	members.sort()

	print html.header('Members of group %s' % group)
	print '<p>Back to <a href="%s/authz">Authz management</a></p>' % _base(input)

	if input.get.has_key('msg'):
		print '<p class="msg">%s</p>' % input.get['msg'][-1]

	print '<h2>Members of group %s</h2>' % group
	print '''
	<form action="%s/authz/delmembers" method="post">
		<input type="hidden" name="group" value="%s" />
		<ul>
	''' % (_base(input), group)
	for member in members:
		print '\t\t\t<li><input type="checkbox" name="%s" value="1" /> %s</li>' %\
			(member, member)
	print '''
		</ul>
		<input type="submit" value="Delete checked members" />
	</form>
	<h2>Add a member</h2>
	<form action="%s/authz/addmember" method="post">
		<input type="hidden" name="group" value="%s" />
		<input type="text" name="member" />
		<input type="submit" value="Add member" />
	</form>''' % (_base(input), group)
	print html.footer()

def delmembers(input):
	authz = _getauthz(input)
	group = input.post['group']
	members = authz.members(group)
	for member in input.post:
		if member != 'group':
			if member not in members:
				continue
			authz.removeMember(group, member)
	raise exceptions.Redirect, '%s/authz/group?group=%s&msg=Members+deleted' %\
			(_base(input), group)

def addmember(input):
	authz = _getauthz(input)
	group = input.post['group']
	member = input.post['member']
	if not member:
		raise exceptions.Redirect, \
				'%s/authz/group?group=%s&msg=Please+fill+in+the+member+field' % \
				(_base(input), group)
	authz.addMember(group, member)
	raise exceptions.Redirect, '%s/authz/group?group=%s&msg=Members+added' %\
			(_base(input), group)

def addgroup(input):
	authz = _getauthz(input)
	group = input.post['newgroup']
	if not group:
		raise exceptions.Redirect, \
				'%s/authz?msg=Please+fill+in+the+group+field' % \
				(_base(input), group)

	authz.addGroup(group)
	raise exceptions.Redirect, '%s/authz/group?group=%s&msg=Group+added' %\
			(_base(input), group)
