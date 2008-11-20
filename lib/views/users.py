from dispatch.view import View
from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse, XMLTemplateResponse
from views.error import ErrorResponse
from models.user import *
from models.group import Group
from auth.decorators import *
from config.authz.authz import UnknownUserError

class Users(View):
	@login_required
	def handler(self, req, path):
		localvars = {}
		config = Config()

		if req.is_ajax():
			return self.ajaxhandler(req, path)

		if len(path) < 1:
			return ErrorResponse('Invalid path', request=req)

		if len(path) > 0:
			localvars['selected_type'] = 'users'
		if len(path) > 1:
			localvars['selected_object'] = path[1]

		try:
			if path[0] == 'show':
				return self.show(req, path[1:], localvars)
			if path[0] == 'add':
				return self.add(req, path[1:], localvars)
		except Unauthorized:
			return Redirect(config.base_url)

		return ErrorResponse('Unknown path', request=req)

	def show(self, req, path, localvars):
		if len(path) < 1:
			return ErrorResponse('Invalid path', request=req)

		is_admin = req.session['user'].is_admin
		if not is_admin and path[0] != req.session['user'].name:
			raise Unauthorized('Permission denied to view this user')

		try:
			user = User(path[0])
		except (IndexError, UnknownUserError):
			return ErrorResponse('This user does not exist.', request=req)

		localvars['user'] = user
		formatted = evaluate_main('users.html', localvars, request=req)
		return Response(formatted)

	def showAddForm(self, req, username, email, fullname, errormsg=''):
		localvars = {}
		localvars['errormsg'] = errormsg
		localvars['username'] = username
		localvars['email'] = email
		localvars['fullname'] = fullname
		formatted = evaluate_main('newuser.html', localvars, request=req)
		return Response(formatted)

	@admin_required
	def add(self, req, path, localvars):
		config = Config()
		base_url = config.base_url
		username = ''
		email = ''
		fullname = ''

		if req.post and req.post['username'] and req.post['email'] and req.post['fullname']:
			import re

			username = req.post['username'].value.strip()
			email = req.post['email'].value.strip()
			fullname = req.post['fullname'].value.strip()
			if re.findall('[^a-zA-Z0-9_-]', username):
				return self.showAddForm(req, username, email, fullname,
					'Invalid characters in username')

			if username == '':
				return self.showAddForm(req, username, email, fullname,
					'Username not supplied')
			if config.htpasswd.exists(username):
				return self.showAddForm(req, username, email, fullname,
					'User already exists')

			if email == '':
				return self.showAddForm(req, username, email, fullname,
					'Email must be supplied')

			if not isEmailValid(email):
				return self.showAddForm(req, username, email, fullname,
					"Email is not valid")

			try:
				addUser(username)
				User(username).setEmail(email)
				User(username).setFullName(fullname)
			except IOError:
				return ErrorResponse('File permission denied', request=req)
			except UserExists:
				return self.showAddForm(req, username, email, fullname,
					'User %s already exists' % username)

			url = base_url + '/users/show/' + username
			return Redirect(url)

		return self.showAddForm(req, username, email, fullname)

	def ajaxhandler(self, req, path):
		username = ''

		if len(path) < 2:
			return XMLStatusResponse('', False, 'Invalid path')

		action = path[0]
		username = path[1]

		if action == 'delete':
			return self.removeUser(req, username)

		user = User(username)
		
		if 'fullname' in req.post and req.post['fullname'].value.strip():
			return self.setFullName(req, user)
		
		if 'email' in req.post and req.post['email'].value.strip():
			return self.setEmail(req, user)

		if 'password' in req.post and req.post['password'].value.strip():
			return self.setPassword(req, user)

		if 'addToGroup' in req.post:
			return self.addToGroup(req, user)

		if 'removeFromGroup' in req.post:
			return self.removeFromGroup(req, user)

		if 'listUserGroups' in req.post:
			return self.listUserGroups(req, user)

		if 'listNotifications' in req.post:
			return self.listNotifications(req, user)
		
		if 'saveNotifications' in req.post:
			return self.saveNotifications(req, user)

		return XMLStatusResponse('', False, 'Unknown command')

	def setEmail(self, req, user):
		try:
			user.email = req.post.get('email')
			return XMLStatusResponse('setEmail', True,
				'Changed email address for user %s to %s' %
				(user.name, user.email))
		except InvalidEmail:
			return XMLStatusResponse('setEmail', False,
				'Invalid email. If you think this is an error, please report a bug')
		except Exception, e:
			return XMLStatusResponse('setEmail', False,
				'Could not change email of user %s: %s' % (user.name, str(e)))
  
	def setFullName(self, req, user):
		try:
			user.fullname = req.post.get('fullname')
			return XMLStatusResponse('setFullName', True,
				'Changed name for user %s to %s' %
				(user.name, user.fullname))
		except InvalidFullName, e:
			return XMLStatusResponse('setFullName', False, str(e))
		except Exception, e:
			return XMLStatusResponse('setFullName', False,
				'Could not change name of user %s: %s' % (user.name, str(e)))

	def setPassword(self, req, user):
		try:
			user.password = req.post.get('password')
			return XMLStatusResponse('setPassword', True,
				'Changed password for user %s' % user.name)
		except Exception, e:
			return XMLStatusResponse('setPassword', False,
				'Could not change password of user %s' % user.name)

	@admin_required
	def addToGroup(self, req, user):
		group = Group(req.post.get('addToGroup'))
		success = group.addMember(user.name)
		msgs = {True: 'User %s added to group %s' % (user.name, group.name),
				False: 'User %s already in group %s' % (user.name, group.name)
				}
		return XMLStatusResponse('addToGroup', success, msgs[success])

	def listUserGroups(self, req, user):
		if req.session['user'].is_admin:
			return XMLTemplateResponse("ajax/usermemberof.xml",
					{"memberof": user.member_of,
						"nonmemberof": user.nonmember_of, "user": user.name})

		if req.session['user'].name != user.name:
			return XMLStatusResponse('listUserGroups', False, "You do not have permission to "
					"view this user.")

		return XMLTemplateResponse("ajax/usermemberof.xml",
				{"memberof": user.member_of, "nonmemberof": [],
					"user": user.name})

	def listNotifications(self, req, user):
		is_admin = req.session['user'].is_admin
		if not is_admin and req.session['user'].name != user.name:
			return XMLStatusResponse('listNotifications', False, "You do not have permission to "
					"view this user.")

		return XMLTemplateResponse("ajax/usernotifications.xml",
				{"notifications": user.notifications, "user": user.name,
					"is_admin": is_admin})

	def saveNotifications(self, req, user):
		is_admin = req.session['user'].is_admin
				
		notifications_str = req.post.get('saveNotifications').split(':')
		notifications = {}
		for n_str in notifications_str:
			n = n_str.split(',')
			try:
				allowed = (n[1] == "true")
				enabled = (n[2] == "true")
				user.setNotification(n[0], dict(allowed=allowed, enabled=enabled), is_admin)
			except NotAuthorized, e:
				return XMLStatusResponse('saveNotifications', False, str(e))
					
		user.saveNotifications()
		
		return XMLStatusResponse("saveNotifications", True, "Saved notifications for user " + user.name)

	@admin_required
	def removeFromGroup(self, req, user):
		group = Group(req.post.get('removeFromGroup'))
		# TODO: Make this a setting in submin.conf?
		if group.name == "submin-admins" and user.name == req.session['user'].name:
			return XMLStatusResponse('removeFromGroup', False,
					"You cannot remove yourself from %s" % group.name)

		success = group.removeMember(user.name)
		msgs = {True: 'User %s removed from group %s' % (user.name, group.name),
				False: 'User %s is not a member of %s' % (user.name, group.name)
				}
		return XMLStatusResponse('removeFromGroup', success, msgs[success])

	@admin_required
	def removeUser(self, req, username):
		if username == req.session['user'].name:
			return XMLStatusResponse('removeUser', False,
				'You are not allowed to delete yourself')
		try:
			user = User(username)
			user.remove()
		except Exception, e:
			return XMLStatusResponse('removeUser', False,
				'User %s not deleted: %s' % (username, str(e)))

		return XMLStatusResponse('removeUser', True, 'User %s deleted' % username)
