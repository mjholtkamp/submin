from dispatch.view import View
from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse
from views.error import ErrorResponse
from models.user import User
from models.group import Group
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

		if path[0] == 'delete':
			return self.delete(req, path[1:])

		return ErrorResponse('Unknown path')

	def show(self, req, path):
		localvars = {}
		try:
			group = Group(path[0])
		except (IndexError, Group.DoesNotExist):
			return ErrorResponse('This group does not exist.')

		localvars['group'] = group
		formatted = evaluate_main('groups', localvars)
		return Response(formatted)

	def add(self, req, path):
		return ErrorResponse('Not yet implemented')

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
			self.removeGroup(groupname)

		if 'removeMember' in req.post:
			return self.removeMember(req, groupname)

		if 'addMember' in req.post:
			return self.addMember(req, groupname)

		error = 'operations for groups are not yet implemented'

		if success:
			response = XMLStatusResponse(True, 'Success')
		else:
			response = XMLStatusResponse(False, error)

		return response

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

	def addMember(self, req, groupname):
		success = Group(groupname).addMember(\
				req.post['addMember'].value)
		msgs = {True: 'Success', False: 'This member already is in this group'}
		return XMLStatusResponse(success, msgs[success])

	def removeUser(self, group):
		return XMLStatusResponse(False, 'Group %s not deleted' % group)
