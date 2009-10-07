from dispatch.view import View
from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse, XMLTemplateResponse
from views.error import ErrorResponse
from models.user import User
from models.group import Group
from models.exceptions import GroupExistsError, MemberExistsError
from auth.decorators import *
from models.options import Options

class Groups(View):
	@login_required
	def handler(self, req, path):
		localvars = {}
		o = Options()

		if req.is_ajax():
			return self.ajaxhandler(req, path)

		if len(path) < 1:
			return ErrorResponse('Invalid path', request=req)

		if len(path) > 0:
			localvars['selected_type'] = 'groups'
		if len(path) > 1:
			localvars['selected_object'] = path[1]

		try:
			if path[0] == 'show':
				return self.show(req, path[1:], localvars)
			if path[0] == 'add':
				return self.add(req, path[1:], localvars)
		except Unauthorized:
			return Redirect(o.url_path('base_url_submin'))

		return ErrorResponse('Unknown path', request=req)

	def show(self, req, path, localvars):
		if len(path) < 1:
			return ErrorResponse('Invalid path', request=req)

		is_admin = req.session['user'].is_admin
		try:
			group = Group(path[0])
		except (IndexError, UnknownGroupError):
			if not is_admin:
				return ErrorResponse('Not permitted', request=req)

			return ErrorResponse('This group does not exist.', request=req)

		if not is_admin and req.session['user'].name not in group.members():
			return ErrorResponse('Not permitted', request=req)

		localvars['group'] = group
		formatted = evaluate_main('groups.html', localvars, request=req)
		return Response(formatted)

	def showAddForm(self, req, groupname, errormsg=''):
		localvars = {}
		localvars['errormsg'] = errormsg
		localvars['groupname'] = groupname
		formatted = evaluate_main('newgroup.html', localvars, request=req)
		return Response(formatted)

	@admin_required
	def add(self, req, path, localvars):
		o = Options()
		base_url = o.url_path('base_url_submin')
		groupname = ''

		if req.post and req.post['groupname']:
			import re

			groupname = req.post['groupname'].value.strip()
			if re.findall('[^a-zA-Z0-9_-]', groupname):
				return self.showAddForm(req, groupname, 'Invalid characters in groupname')
			if groupname == '':
				return self.showAddForm(req, groupname, 'Groupname not supplied')

			url = base_url + '/groups/show/' + groupname

			try:
				Group.add(groupname)
			except IOError:
				return ErrorResponse('File permission denied', request=req)
			except GroupExistsError:
				return self.showAddForm(req, groupname, 'Group %s already exists' % groupname)

			return Redirect(url)

		return self.showAddForm(req, groupname)

	def ajaxhandler(self, req, path):
		success = False
		error = ''
		response = None
		username = ''

		if len(path) < 2:
			return XMLStatusResponse('', False, 'Invalid Path')

		action = path[0]
		groupname = path[1]

		if action == 'delete':
			return self.removeGroup(groupname)

		if 'removeMember' in req.post:
			return self.removeMember(req, groupname)

		if 'addMember' in req.post:
			return self.addMember(req, groupname)

		if 'listGroupUsers' in req.post:
			return self.listGroupUsers(req, Group(groupname))

		return XMLStatusResponse('', False, 'Unknown command')

	def listGroupUsers(self, req, group):
		members = list(group.members())
		if req.session['user'].is_admin:
			nonmembers = []
			usernames = User.list(req.session['user'])
			for username in usernames:
				if username not in members:
					nonmembers.append(username)

			return XMLTemplateResponse("ajax/groupmembers.xml",
					{"members": members, "nonmembers": nonmembers,
						"group": group.name})

		if req.session['user'].name not in group.members():
			return XMLStatusResponse('listGroupUsers', False,
				"You do not have permission to view this group.")

		return XMLTemplateResponse("ajax/groupmembers.xml",
				{"members": members, "nonmembers": [],
					"group": group.name})

	@admin_required
	def removeMember(self, req, groupname):
		group = Group(groupname)
		username = req.post['removeMember'].value
		success = True
		try:
			Group(groupname).remove_member(User(username))
		except:
			success = False

		msgs = {True: 'User %s removed from group %s' % (username, groupname),
				False: 'User %s is not a member of group %s' % (username, groupname)}
		return XMLStatusResponse('removeMember', success, msgs[success])

	@admin_required
	def addMember(self, req, groupname):
		username = req.post['addMember'].value
		success = True
		try:
			Group(groupname).add_member(User(username))
		except MemberExistsError:
			success = False

		msgs = {True: 'User %s added to group %s' % (username, groupname),
				False: 'User %s already in group %s' % (username, groupname)}
		return XMLStatusResponse('addMember', success, msgs[success])

	@admin_required
	def removeGroup(self, groupname):
		try:
			group = Group(groupname)
			group.remove()
		except IOError:
			return XMLStatusResponse('removeGroup', False, 'File permisson denied')
		except UnknownGroupError:
			return XMLStatusResponse('removeGroup', False,
				'Group %s does not exist' % groupname)

		return XMLStatusResponse('removeGroup', True, 'Group %s deleted' % group)

