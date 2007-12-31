from dispatch.view import View
from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse
from views.error import ErrorResponse
from models.user import User
from models.group import Group, addGroup
from config.authz.authz import GroupExistsError, UnknownGroupError
from auth.decorators import *

class Groups(View):
	@login_required
	def handler(self, req, path):
		if req.is_ajax():
			return self.ajaxhandler(req, path)

		if path[0] == 'show':
			return self.show(req, path[1:])

		if path[0] == 'add':
			return self.add(req, path[1:])

		return ErrorResponse('Unknown path', request=req)

	def show(self, req, path):
		localvars = {}
		try:
			group = Group(path[0])
		except (IndexError, Group.DoesNotExist):
			return ErrorResponse('This group does not exist.', request=req)

		localvars['group'] = group
		formatted = evaluate_main('groups', localvars, request=req)
		return Response(formatted)

	@admin_required
	def add(self, req, path):
		config = Config()
		media_url = config.get('www', 'media_url').rstrip('/')

		if req.post and req.post['groupname']:
			groupname = req.post['groupname'].value.strip()
			url = media_url + '/groups/show/' + groupname

			try:
				addGroup(groupname)
			except IOError:
				return ErrorResponse('File permission denied', request=req)
			except GroupExistsError:
				return ErrorResponse('Group already exists', request=req)

			return Redirect(url)

		localvars = {}
		formatted = evaluate_main('newgroup', localvars, request=req)
		return Response(formatted)

	def ajaxhandler(self, req, path):
		success = False
		error = ''
		response = None
		username = ''

		if len(path) < 2:
			return XMLStatusResponse(False, 'Invalid Path')

		action = path[0]
		groupname = path[1]

		if action == 'delete':
			return self.removeGroup(groupname)

		if 'removeMember' in req.post:
			return self.removeMember(req, groupname)

		if 'addMember' in req.post:
			return self.addMember(req, groupname)

		return XMLStatusResponse(False, 'You tried to submit an empty field value')

	@admin_required
	def removeMember(self, req, groupname):
		group = Group(groupname)
		username = req.post['removeMember'].value
		# TODO: Make this a setting in submin.conf?
		if group.name == "submin-admins" and username == req.session['user'].name:
			return XMLStatusResponse(False,
					"You cannot remove yourself from %s" % group.name)

		success = Group(groupname).removeMember(\
				req.post['removeMember'].value)
		msgs = {True: 'Success', False: 'No such user'}
		return XMLStatusResponse(success, msgs[success])

	@admin_required
	def addMember(self, req, groupname):
		success = Group(groupname).addMember(\
				req.post['addMember'].value)
		msgs = {True: 'Success', False: 'This member already is in this group'}
		return XMLStatusResponse(success, msgs[success])

	@admin_required
	def removeGroup(self, groupname):
		if groupname == 'submin-admins':
			return XMLStatusResponse(False, 'You are not allowed to delete the submin-admins group')

		try:
			group = Group(groupname)
			group.remove()
		except IOError:
			return XMLStatusResponse(False, 'File permisson denied')
		except UnknownGroupError:
			return XMLStatusResponse(False, 'Group %s does not exist' % groupname)

		return XMLStatusResponse(True, 'Group %s deleted' % group)