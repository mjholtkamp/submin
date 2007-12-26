from dispatch.view import View
from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse
from views.error import ErrorResponse
from models.user import User
from models.group import Group
from auth.decorators import *

class Users(View):
	@login_required
	def handler(self, req, path):
		if req.is_ajax():
			return self.ajaxhandler(req, path)

		localvars = {}

		try:
			user = User(path[0])
		except (IndexError, User.DoesNotExist):
			return ErrorResponse('This user does not exist.')

		localvars['user'] = user
		formatted = evaluate_main('users', localvars)
		return Response(formatted)

	def ajaxhandler(self, req, path):
		username = ''

		if len(path) > 0:
			username = path[0]

		user = User(username)

		if 'email' in req.post and req.post['email'].value.strip():
			return self.setEmail(req, user)

		if 'password' in req.post and req.post['password'].value.strip():
			return self.setPassword(req, user)

		if 'addToGroup' in req.post:
			return self.addToGroup(req, user)

		if 'removeFromGroup' in req.post:
			return self.removeFromGroup(req, user)

		return XMLStatusResponse(False, 'You tried to submit an empty field value')

	def setEmail(self, req, user):
		try:
			user.email = req.post.get('email')
			return XMLStatusResponse(True, 'Success!')
		except Exception, e:
			return XMLStatusResponse(False, 'Could not change email of user ' + user.name)

	def setPassword(self, req, user):
		try:
			user.password = req.post.get('password')
			return XMLStatusResponse(True, 'Success!')
		except Exception, e:
			return XMLStatusResponse(False, 'Could not change password of user ' + user.name)

	def addToGroup(self, req, user):
		group = Group(req.post.get('addToGroup'))
		success = group.addMember(user.name)
		msgs = {True: 'Success', False: 'This user is already in group %s' % group.name}
		return XMLStatusResponse(success, msgs[success])

	def removeFromGroup(self, req, user):
		group = Group(req.post.get('removeFromGroup'))
		# TODO: Make this a setting in submin.conf?
		if group.name == "submin-admins" and user.name == req.session['user'].name:
			return XMLStatusResponse(False,
					"You cannot remove yourself from %s" % group.name)

		success = group.removeMember(user.name)
		msgs = {True: 'Success', False: 'User was not a member of %s' % group.name}
		return XMLStatusResponse(success, msgs[success])
