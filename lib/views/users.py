from dispatch.view import View
from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse, XMLTemplateResponse
from views.error import ErrorResponse
from models.user import User, addUser, UserExists
from models.group import Group
from auth.decorators import *
from config.authz.authz import UnknownUserError

class Users(View):
	@login_required
	def handler(self, req, path):
		localvars = {}

		if req.is_ajax():
			return self.ajaxhandler(req, path)

		if len(path) < 1:
			return ErrorResponse('Invalid path', request=req)

		if len(path) > 0:
			localvars['selected_type'] = 'users'
		if len(path) > 1:
			localvars['selected_object'] = path[1]

		if path[0] == 'show':
			return self.show(req, path[1:], localvars)

		if path[0] == 'add':
			return self.add(req, path[1:], localvars)

		return ErrorResponse('Unknown path', request=req)

	def show(self, req, path, localvars):
		if len(path) < 1:
			return ErrorResponse('Invalid path', request=req)

		is_admin = req.session['user'].is_admin
		if not is_admin and path[0] != req.session['user'].name:
			return ErrorResponse('Permission denied to view this user',
					request=req)

		try:
			user = User(path[0])
		except (IndexError, UnknownUserError):
			return ErrorResponse('This user does not exist.', request=req)

		localvars['user'] = user
		formatted = evaluate_main('users.html', localvars, request=req)
		return Response(formatted)

	@admin_required
	def add(self, req, path, localvars):
		config = Config()
		media_url = config.get('www', 'media_url').rstrip('/')

		if req.post and req.post['username']:
			import re

			username = req.post['username'].value.strip()
			if re.findall('[^a-zA-Z0-9_]', username):
				return ErrorResponse('Invalid characters in username', request=req)
			url = media_url + '/users/show/' + username
			try:
				addUser(username)
			except IOError:
				return ErrorResponse('File permission denied', request=req)
			except UserExists:
				return ErrorResponse('User %s already exists' % username, request=req)

			return Redirect(url)

		formatted = evaluate_main('newuser.html', localvars, request=req)
		return Response(formatted)

	def ajaxhandler(self, req, path):
		username = ''

		# list doesn't need any arguments
		if 'list' in req.post:
			return self.list(req)

		if len(path) < 2:
			return XMLStatusResponse(False, 'Invalid path')

		action = path[0]
		username = path[1]

		if action == 'delete':
			return self.removeUser(req, username)

		user = User(username)

		if 'email' in req.post and req.post['email'].value.strip():
			return self.setEmail(req, user)

		if 'password' in req.post and req.post['password'].value.strip():
			return self.setPassword(req, user)

		if 'addToGroup' in req.post:
			return self.addToGroup(req, user)

		if 'removeFromGroup' in req.post:
			return self.removeFromGroup(req, user)

		if 'initSelector' in req.post:
			return self.initSelector(req, user)

		return XMLStatusResponse(False,
			'You tried to submit an empty field value')

	def setEmail(self, req, user):
		try:
			user.email = req.post.get('email')
			return XMLStatusResponse(True,
				'Changed email address for user %s to %s' %
				(user.name, user.email))

		except Exception, e:
			return XMLStatusResponse(False,
				'Could not change email of user %s' + user.name)

	def setPassword(self, req, user):
		try:
			user.password = req.post.get('password')
			return XMLStatusResponse(True,
				'Changed password for user %s' % user.name)
		except Exception, e:
			return XMLStatusResponse(False,
				'Could not change password of user %s' % user.name)

	@admin_required
	def list(self, req):
		try:
			config = Config()
			users = config.htpasswd.users()
			return XMLTemplateResponse("ajax/listusers.xml", {'users': users})
		except Exception, e:
			return XMLStatusResponse(False, 'Failed to get a list: %s' % e)

	@admin_required
	def addToGroup(self, req, user):
		group = Group(req.post.get('addToGroup'))
		success = group.addMember(user.name)
		msgs = {True: 'User %s added to group %s' % (user.name, group.name),
				False: 'User %s already in group %s' % (user.name, group.name)
				}
		return XMLStatusResponse(success, msgs[success])

	def initSelector(self, req, user):
		if req.session['user'].is_admin:
			return XMLTemplateResponse("ajax/usermemberof.xml",
					{"memberof": user.member_of,
						"nonmemberof": user.nonmember_of, "user": user.name})

		if req.session['user'].name != user.name:
			return XMLStatusResponse(False, "You do not have permission to "
					"view this user.")

		return XMLTemplateResponse("ajax/usermemberof.xml",
				{"memberof": user.member_of, "nonmemberof": [],
					"user": user.name})

	@admin_required
	def removeFromGroup(self, req, user):
		group = Group(req.post.get('removeFromGroup'))
		# TODO: Make this a setting in submin.conf?
		if group.name == "submin-admins" and user.name == req.session['user'].name:
			return XMLStatusResponse(False,
					"You cannot remove yourself from %s" % group.name)

		success = group.removeMember(user.name)
		msgs = {True: 'User %s removed from group %s' % (user.name, group.name),
				False: 'User %s is not a member of %s' % (user.name, group.name)
				}
		return XMLStatusResponse(success, msgs[success])

	@admin_required
	def removeUser(self, req, username):
		if username == req.session['user'].name:
			return XMLStatusResponse(False,
				'You are not allowed to delete yourself')
		try:
			user = User(username)
			user.remove()
		except Exception, e:
			return XMLStatusResponse(False,
				'User %s not deleted: %s' % (username, str(e)))

		return XMLStatusResponse(True, 'User %s deleted' % username)
