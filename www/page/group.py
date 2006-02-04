import urllib
from lib.utils import mimport
mod_authz = mimport('lib.authz')
exceptions = mimport('lib.exceptions')
mod_htpasswd = mimport('lib.htpasswd')

admin = True

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

def handler(input):
	if input.get.has_key('group'):
		return _showgroup(input)

	msg = None
	if input.get.has_key('msg'):
		msg = input.get['msg'][-1]

	authz = _getauthz(input)

	print input.html.header('Permissions')

	if msg:
		print '<p class="msg">%s</p>' % msg

	print '''<h2>Groups</h2>
<table>
	<thead>
		<td style="width: 20px"></td>
		<th style="width: 150px" align="left">Group</th>
		<th align="left">Members</th>
	</thead>
	<form action="%s/group/delgroup" method="post" onsubmit="return confirm('Do you really want to delete these groups? (there is no undo!)')">
''' % input.base
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
		(group, input.base, urllib.quote(group), group, 
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
	<form action="%s/group/add" method="post">
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
</table>''' % input.base

	print input.html.footer()


def _showgroup(input):
	authz = _getauthz(input)
	group = input.get['group'][-1]
	members = authz.members(group)
	members.sort()

	print input.html.header('Members of group %s' % group)

	if input.get.has_key('msg'):
		print '<p class="msg">%s</p>' % input.get['msg'][-1]

	print '<h2>Members of group %s</h2>' % group
	print '''
	<form action="%s/group/delmembers" method="post">
		<input type="hidden" name="group" value="%s" />
		<ul>
	''' % (input.base, group)
	for member in members:
		print '\t\t\t<li><input type="checkbox" name="%s" value="1" id="group_%s" /> <label for="group_%s">%s</label></li>' %\
			(member, member, member, member)
	print '''
		</ul>
		<input type="submit" value="Delete checked members" />
	</form>
	<h2>Add a member</h2>
	<form action="%s/group/addmember" method="post">
		<select class="form" name="member">
			<option value="">Choose a user</option>
	''' % input.base

	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	users = htpasswd.users()

	for user in users:
		print '<option value="%s">%s</option>' % (user, user)

	print '''
		</select>
		<input type="hidden" name="group" value="%s" />
		<input type="submit" value="Add member" />
	</form>''' % group
	print input.html.footer()

def delmembers(input):
	authz = _getauthz(input)
	group = input.post['group']
	members = authz.members(group)
	for member in input.post:
		if member != 'group':
			if member not in members:
				continue
			authz.removeMember(group, member)
	raise exceptions.Redirect, '%s/group?group=%s&msg=Members+deleted' %\
			(input.base, group)

def addmember(input):
	authz = _getauthz(input)
	group = input.post['group']
	member = input.post['member']
	if not member:
		raise exceptions.Redirect, \
				'%s/group?group=%s&msg=Please+fill+in+the+member+field' % \
				(input.base, group)
	authz.addMember(group, member)
	raise exceptions.Redirect, '%s/group?group=%s&msg=Members+added' %\
			(input.base, group)

def add(input):
	authz = _getauthz(input)
	group = input.post['newgroup']
	if not group:
		raise exceptions.Redirect, \
				'%s/group?msg=Please+fill+in+the+group+field' % \
				(input.base, group)

	authz.addGroup(group)
	raise exceptions.Redirect, '%s/group?group=%s&msg=Group+added' %\
			(input.base, group)

def delgroup(input):
	authz = _getauthz(input)
	for group in input.post:
		try:
			authz.removeGroup(group)
		except mod_authz.UnknownGroupError:
			pass

	raise exceptions.Redirect, '%s/group?msg=Groups+deleted' % input.base


