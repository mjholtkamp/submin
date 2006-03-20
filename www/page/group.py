import urllib
from lib.utils import mimport
mod_authz = mimport('lib.authz')
exceptions = mimport('lib.exceptions')
mod_htpasswd = mimport('lib.htpasswd')

admin = True
login_required = True

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

	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	users = htpasswd.users()
	users.sort()

	print input.html.header('Permissions')

	if msg:
		print '<p class="msg">%s</p>' % msg

	print '''
	<script type="text/javascript">
      reverteffect = function(element, top_offset, left_offset) {
		var dur = 1;
        element._revert = new Effect.Move(element, { x: -left_offset, y: -top_offset, duration: dur});
      }
	</script>'''

	users = ['<li><span id="user_%s" class="users"><img src="images/user.png" />%s</span></li><script type="text/javascript">new Draggable(\'user_%s\', {revert:true, reverteffect:reverteffect})</script>' % \
			(user, user, user) for user in users]
	print '''<br />
	<div style="position: fixed; top:20px; right: 20px; width: 205px">
	<div id="wastebin"></div>
	<fieldset id="users">
		<legend>Users</legend>
		<ul>%s</ul>
	</fieldset>
	</div>''' % '\n'.join(users)

	print '''
	<p id="indicator" style="display:none">
		<img alt="Indicator" src="images/indicator.gif" style="vertical-align: center"/> Updating groups...
	</p>
	'''
	print '''<script type="text/javascript">
Droppables.add('wastebin', {accept:['members','groups'],
onDrop:function(element){
	if (element.className == 'members')
	{
		idx = element.id.lastIndexOf('=');
		group = element.id.substring(0, idx);
		member = element.id.substring(idx + 1, element.id.length);
		new Ajax.Updater(group, 'group/ajax_delmember', 
			{method: 'get', parameters:'group=' + encodeURIComponent(group) + '&member=' + encodeURIComponent(member), 
			 evalScripts:true, asynchronous:true,
			 onLoading:function(request){Element.show('indicator')}, onComplete:function(request){Element.hide('indicator')}
			});
		Element.hide(element);
	}
	else if (element.className == 'groups')
	{
		if (!confirm("Do you really want to delete this group? There is no undo!"))
			return;

		idx = element.id.indexOf('group_');
		group = element.id.substring(idx + 6, element.id.length);
		new Ajax.Updater(group, 'group/ajax_delgroup', 
			{method: 'get', parameters:'group=' + encodeURIComponent(group), 
			 evalScripts:true, asynchronous:true,
			 onLoading:function(request){Element.show('indicator')}, onComplete:function(request){Element.hide('indicator')}
			 });
		Element.hide($('fs_' + group));
	}
}, 
hoverclass:'wastebin-active'})
</script>
	'''
	print '''<h2>Groups</h2>'''
	groups = authz.groups()
	groups.sort()
	for group in groups:
		members = authz.members(group)
		members.sort()
		members = ['<span id="%s=%s" class="members"><img src="images/user.png" />%s</span><script type="text/javascript">new Draggable(\'%s=%s\', {revert:true})</script>' % \
				(group, member, member, group, member) for member in members]
		print '''\t<fieldset id="fs_%s">
		<legend><span id="group_%s" class="groups"><img src="images/group.png" />%s</span></legend>
		<div id="%s" style="min-height: 15px">%s</div>
	</fieldset>''' % \
		(group, group, group, group, ', '.join(members))

		print '''
		<script type="text/javascript">
		new Draggable(\'group_%s\', {revert:true});
		Droppables.add('%s', {accept:'users',
		onDrop:function(element){
			idx = element.id.lastIndexOf('_');
			member = element.id.substring(idx + 1, element.id.length);
			new Ajax.Updater('%s', 'group/ajax_addmember', 
				{method: 'get', parameters:'group=' + encodeURIComponent('%s') + '&member=' + encodeURIComponent(member), 
				 evalScripts:true, asynchronous:true,
				 onLoading:function(request){Element.show('indicator')}, onComplete:function(request){Element.hide('indicator')}
				 });
},
		hoverclass:'wastebin-active'})
		</script>
		''' % (group, group, group, group)

	print '''
<h3>Add a group</h3>
<table>
	<form action="%sgroup/add" method="post">
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

def _oldshouwgroup():
	print '''
	<form action="%sgroup/delmembers" method="post">
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
	<form action="%sgroup/addmember" method="post">
		<select class="form" name="member">
			<option value="">Choose a user</option>
	''' % input.base

	for user in users:
		print '<option value="%s">%s</option>' % (user, user)

	print '''
		</select>
		<input type="hidden" name="group" value="%s" />
		<input type="submit" value="Add member" />
	</form>''' % group

def _showgroup(input):
	authz = _getauthz(input)
	group = input.get['group'][-1]
	members = authz.members(group)
	members.sort()

	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	users = htpasswd.users()

	print input.html.header('Members of group %s' % group, 
			css=["group"], scripts=["group"])

	if input.get.has_key('msg'):
		print '<p class="msg">%s</p>' % input.get['msg'][-1]

	print '<h2>Members of group %s</h2>' % group

	print '''
	<div id="grouphug">
	<form action="group/savemember" method="post">
		<input type="hidden" name="group" value="%s" />
		<div id="d_ingroup">
			<p>Users in group %s</p>
			<select name="ingroup" multiple="multiple" style="width: 150px; height: 200px;">
		''' % \
				(group, group)
	for member in members:
		print '\t\t\t\t<option value="%s">%s</option>' % (member, member)
	print '''
			</select>
		</div>

		<div id="d_outgroup">
			<p>Users not in group %s</p>
			<select name="outgroup" multiple="multiple" style="width: 150px; height: 200px;">
		''' % group

	for user in users:
		if user not in members:
			print '\t\t\t\t<option value="%s">%s</option>' % (user, user)
	
	print '''
			</select>
		</div>

		<div id="buttons">
			<input type="button" name="b_movein" value="<-"  onclick="movein(this.form)"  />
			<input type="button" name="b_moveout" value="->" onclick="moveout(this.form)" />
		</div>


		<div id="groupsubmit">
			<input type="submit" value="Save members" onclick="selectAllIn(this.form)" />
		</div>
	</form>
	</div>'''

# End test for new interface

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
	raise exceptions.Redirect, '%sgroup?group=%s&msg=Members+deleted' %\
			(input.base, group)

def addoldmember(input):
	authz = _getauthz(input)
	group = input.post['group']
	member = input.post['member']
	if not member:
		raise exceptions.Redirect, \
				'%sgroup?group=%s&msg=Please+fill+in+the+member+field' % \
				(input.base, group)
	authz.addMember(group, member)
	raise exceptions.Redirect, '%sgroup?group=%s&msg=Members+added' %\
			(input.base, group)

def savemember(input):
	authz = _getauthz(input)
	group = input.post['group']
	authz.removeAllMembers(group)
	for member in input.post['ingroup']:
		authz.addMember(group, member)
	raise exceptions.Redirect, '%sgroup?group=%s&msg=Members+saved' %\
			(input.base, group)

def add(input):
	authz = _getauthz(input)
	group = input.post['newgroup']
	if not group:
		raise exceptions.Redirect, \
				'%sgroup?msg=Please+fill+in+the+group+field' % \
				(input.base, group)

	authz.addGroup(group)
	raise exceptions.Redirect, '%sgroup' %\
			(input.base)

def delgroup(input):
	authz = _getauthz(input)
	for group in input.post:
		try:
			authz.removeGroup(group)
		except mod_authz.UnknownGroupError:
			pass

	raise exceptions.Redirect, '%sgroup?msg=Groups+deleted' % input.base

def ajax_delmember(input):
	authz = _getauthz(input)

	group = input.get['group'][0]
	del_member = input.get['member'][0]

	try:
		authz.removeMember(group, del_member)
	except: pass
	members = authz.members(group)
	members.sort()
	#members.remove(del_member)
	members = ['''<span id="%s=%s" class="members"><img src="images/user.png" />%s</span><script type="text/javascript">new Draggable(\'%s=%s\', {revert:true});</script>''' %\
			(group, member, member, group, member) for member in members]
	print ', '.join(members)

def ajax_delgroup(input):
	authz = _getauthz(input)

	group = input.get['group'][0]

	try:
		authz.removeGroup(group)
	except mod_authz.UnknownGroupError:
		pass

	print ' '

def ajax_addmember(input):
	authz = _getauthz(input)

	group = input.get['group'][0]
	add_member = input.get['member'][0]

	try:
		authz.addMember(group, add_member)
	except: pass
	members = authz.members(group)
	members.sort()
	#members.remove(del_member)
	members = ['''<span id="%s=%s" class="members"><img src="images/user.png" />%s</span><script type="text/javascript">new Draggable(\'%s=%s\', {revert:true});</script>''' %\
			(group, member, member, group, member) for member in members]
	print ', '.join(members)
