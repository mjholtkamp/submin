from submin.dispatch.view import View
from submin.template.shortcuts import evaluate_main
from submin.dispatch.response import Response, XMLStatusResponse, XMLTemplateResponse
from submin.views.error import ErrorResponse
from submin.models import user
from submin.models.exceptions import UnknownUserError, UserExistsError, \
		UserPermissionError, MemberExistsError
from submin.models import group
from submin.auth.decorators import *
from submin.models import options
from submin.models import validators

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

		try:
			if path[0] == 'show':
				return self.show(req, path[1:], localvars)
			if path[0] == 'add':
				return self.add(req, path[1:], localvars)
		except Unauthorized:
			return Redirect(options.url_path('base_url_submin'), req)

		return ErrorResponse('Unknown path', request=req)

	def show(self, req, path, localvars):
		if len(path) < 1:
			return ErrorResponse('Invalid path', request=req)

		is_admin = req.session['user']['is_admin']
		if not is_admin and path[0] != req.session['user']['name']:
			raise Unauthorized('Permission denied to view this user')

		try:
			u = user.User(path[0])
		except (IndexError, UnknownUserError):
			return ErrorResponse('This user does not exist.', request=req)

		localvars['user'] = u
		if 'change_password_hint' in req.session:
			localvars['change_password_hint'] = True

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
		import re

		base_url = options.url_path('base_url_submin')
		username = ''
		email = ''
		fullname = ''

		if not req.post or not req.post['username'] \
						or not req.post['email']    \
						or not req.post['fullname']:
			return self.showAddForm(req, username, email, fullname)

		username = req.post.get('username').strip()
		email = req.post.get('email').strip()
		fullname = req.post.get('fullname').strip()
		send_mail = 'send_password' in req.post

		# check these before we add the user, the rest is checked when adding
		try:
			validators.validate_email(email)
			validators.validate_fullname(fullname)
		except validators.InvalidEmail:
			return self.showAddForm(req, username, email, fullname,
				'Email is not valid')
		except validators.InvalidFullname:
			return self.showAddForm(req, username, email, fullname,
				'Invalid characters in full name')

		if username == '':
			return self.showAddForm(req, username, email, fullname,
				'Username not supplied')

		if email == '':
			return self.showAddForm(req, username, email, fullname,
				'Email must be supplied')

		try:
			u = user.add(username, email, send_mail=send_mail, origin=req.remote_address)
			u.fullname = fullname
		except IOError:
			return ErrorResponse('File permission denied', request=req)
		except UserExistsError:
			return self.showAddForm(req, username, email, fullname,
				'User %s already exists' % username)
		except validators.InvalidUsername:
			return self.showAddForm(req, username, email, fullname,
				'Invalid characters in username')

		url = base_url + '/users/show/' + username
		return Redirect(url, req)

	def ajaxhandler(self, req, path):
		username = ''

		if len(path) < 2:
			return XMLStatusResponse('', False, 'Invalid path')

		action = path[0]
		username = path[1]

		if action == 'delete':
			return self.removeUser(req, username)

		u = user.User(username)
		
		if 'fullname' in req.post and req.post.get('fullname').strip():
			return self.setFullName(req, u)
		
		if 'email' in req.post and req.post.get('email').strip():
			return self.setEmail(req, u)

		if 'password' in req.post and req.post.get('password').strip():
			return self.setPassword(req, u)

		if 'sendPasswordMail' in req.post:
			return self.sendPasswordMail(req, u)

		if 'addToGroup' in req.post:
			return self.addToGroup(req, u)

		if 'removeFromGroup' in req.post:
			return self.removeFromGroup(req, u)

		if 'listUserGroups' in req.post:
			return self.listUserGroups(req, u)

		if 'listNotifications' in req.post:
			return self.listNotifications(req, u)

		if 'addSSHKey' in req.post:
			return self.addSSHKey(req, u)

		if 'removeSSHKey' in req.post:
			return self.removeSSHKey(req, u)
		
		if 'saveNotifications' in req.post:
			return self.saveNotifications(req, u)

		if 'listSSHKeys' in req.post:
			return self.listSSHKeys(req, u)
		
		if 'setIsAdmin' in req.post:
			return self.setIsAdmin(req, u)

		return XMLStatusResponse('', False, 'Unknown command')

	def setEmail(self, req, u):
		try:
			u.email = req.post.get('email')
			return XMLStatusResponse('email', True,
				'Changed email address for user %s to %s' %
				(u.name, u.email))
		except validators.InvalidEmail:
			return XMLStatusResponse('email', False,
				'Invalid characters in email-address. If you think this is an error, please report a bug')
		except Exception, e:
			return XMLStatusResponse('email', False,
				'Could not change email of user %s: %s' % (u.name, str(e)))
  
	def setFullName(self, req, u):
		try:
			u.fullname = req.post.get('fullname')
			return XMLStatusResponse('setFullName', True,
				'Changed name for user %s to %s' %
				(u.name, u.fullname))
		except validators.InvalidFullname, e:
			return XMLStatusResponse('setFullName', False, str(e))
		except Exception, e:
			return XMLStatusResponse('setFullName', False,
				'Could not change name of user %s: %s' % (u.name, str(e)))

	def setPassword(self, req, u):
		try:
			u.set_password(req.post.get('password'))
		except Exception, e:
			return XMLStatusResponse('setPassword', False,
				'Could not change password of user %s: %s' % (u.name, e))
		else:
			# User changed their password, we don't have to remind to
			# change the password anymore
			if 'change_password_hint' in req.session:
				del req.session['change_password_hint']
			return XMLStatusResponse('setPassword', True,
				'Changed password for user %s' % u.name)

	def sendPasswordMail(self, req, u):
		try:
			u.prepare_password_reset(req.remote_address)
			return XMLStatusResponse('sendPasswordMail', True,
				'Send password reset email to user %s' % u.name)
		except Exception, e:
			return XMLStatusResponse('sendPasswordMail', False,
				"Could not send Reset password email of user %s: %s" % \
						(u.name, e))

	@admin_required
	def addToGroup(self, req, u):
		g = group.Group(req.post.get('addToGroup'))
		success = True
		try:
			g.add_member(u)
		except MemberExistsError:
			success = False

		msgs = {True: 'User %s added to group %s' % (u.name, g.name),
				False: 'User %s already in group %s' % (u.name, g.name)
				}
		return XMLStatusResponse('addToGroup', success, msgs[success])

	def listUserGroups(self, req, u):
		member_of_names = list(u.member_of())
		session_user = req.session['user']
		if session_user['is_admin']:
			asking_user = user.User(session_user['name'])
			nonmember_of = []
			groupnames = group.list(asking_user)
			for groupname in groupnames:
				if groupname not in member_of_names:
					nonmember_of.append(groupname)
			
			return XMLTemplateResponse("ajax/usermemberof.xml",
					{"memberof": member_of_names,
						"nonmemberof": nonmember_of, "user": u.name})

		if session_user['name'] != u.name:
			return XMLStatusResponse('listUserGroups', False, "You do not have permission to "
					"view this user.")

		return XMLTemplateResponse("ajax/usermemberof.xml",
				{"memberof": member_of_names, "nonmemberof": [],
					"user": u.name})

	def listNotifications(self, req, u):
		session_user = req.session['user']
		if not session_user['is_admin'] and session_user['name'] != u.name:
			return XMLStatusResponse('listNotifications', False, "You do not have permission to "
					"view this user.")

		return XMLTemplateResponse("ajax/usernotifications.xml",
				{"notifications": u.notifications(), "username": u.name,
				"session_user": session_user})

	def listSSHKeys(self, req, u):
		session_user = req.session['user']
		if not session_user['is_admin'] and session_user['name'] != u.name:
			return XMLStatusResponse('listSSHKeys', False, "You do not have permission to "
					"view this user.")

		ssh_keys = u.ssh_keys()

		return XMLTemplateResponse("ajax/usersshkeys.xml",
				{"ssh_keys": ssh_keys, "username": u.name,
				"session_user": session_user})

	def addSSHKey(self, req, u):
		session_user = req.session['user']
		if not session_user['is_admin'] and session_user['name'] != u.name:
			return XMLStatusResponse('addSSHKey', False,
				"You do not have permission to add SSH Keys for this user.")
		title = req.post.get("title", None)
		if not title:
			title = None # user.add_ssh_key will deduct the correct title
		ssh_key = req.post.get("ssh_key")
		if not ssh_key:
			return XMLStatusResponse("addSSHKey", False,
					"Please provide an SSH Key")

		try:
			u.add_ssh_key(ssh_key, title)
			return XMLStatusResponse("addSSHKey", True,
					"SSH Key successfully added.")
		except validators.InvalidSSHKey:
			return XMLStatusResponse('addSSHKey', False,
				'Invalid SSH Key provided. If you think this is an error, please report a bug')

	def removeSSHKey(self, req, u):
		session_user = req.session['user']
		if not session_user['is_admin'] and session_user['name'] != u.name:
			return XMLStatusResponse('addSSHKey', False,
				"You do not have permission to add SSH Keys for this user.")
		ssh_key_id = req.post.get("removeSSHKey")
		if not ssh_key_id:
			return XMLStatusResponse('removeSSHKey', False,
				"Something went wrong with passing the key id to the server.")
		u.remove_ssh_key(ssh_key_id)
		return XMLStatusResponse("removeSSHKey", True,
				"SSH Key successfully removed.")

	def saveNotifications(self, req, u):
		session_user = req.session['user']
		
		notifications_str = req.post.get('saveNotifications').split('|')
		notifications = []
		for n_str in notifications_str:
			try:
				type_repos, enabled = n_str.split(',', 1)
				vcstype, reposname = type_repos.split(':', 1)
			except ValueError:
				return XMLStatusResponse('saveNotifications', False,
					'Badly formatted notifications, reload the page and try again')

			enabled = (enabled == "true")
			notifications.append({'name': reposname, 'vcs': vcstype,
					'enabled': enabled})
		try:
			asking_user = user.User(session_user['name'])
			u.set_notifications(notifications, asking_user)
		except UserPermissionError, e:
			return XMLStatusResponse('saveNotifications', False, str(e))

		return XMLStatusResponse("saveNotifications", True, "Saved notifications for user " + u.name)

	@admin_required
	def removeFromGroup(self, req, u):
		g = group.Group(req.post.get('removeFromGroup'))
		success = True
		try:
			g.remove_member(u)
		except: # XXX except what?!
			succes = False

		msgs = {True: 'User %s removed from group %s' % (u.name, g.name),
				False: 'User %s is not a member of %s' % (u.name, g.name)
				}
		return XMLStatusResponse('removeFromGroup', success, msgs[success])

	@admin_required
	def removeUser(self, req, username):
		if username == req.session['user']['name']:
			return XMLStatusResponse('removeUser', False,
				'You are not allowed to delete yourself')
		try:
			u = user.User(username)
		except UnknownUserError:
			return XMLStatusResponse('removeUser', False,
				"Could not find user '%s'" % username)
		try:
			u.remove()
		except Exception, e:
			return XMLStatusResponse('removeUser', False,
				'User %s not deleted: %s' % (username, str(e)))

		return XMLStatusResponse('removeUser', True, 'User %s deleted' % username)

	@admin_required
	def setIsAdmin(self, req, u):
		is_admin = req.post.get('setIsAdmin')
		if u.name == req.session['user']['name']:
			return XMLStatusResponse('setIsAdmin', False,
				'You are not allowed to change admin rights for yourself')

		try:
			u.is_admin = is_admin
		except Exception, e:
			return XMLStatusResponse('setIsAdmin', False,
				'Could not change admin status for user %s: %s' % (u.name, str(e)))

		newstatus = {'false':'revoked', 'true':'granted'}[is_admin]
		return XMLStatusResponse('setIsAdmin', True, 
			'Admin rights for user %s %s' % (u.name, newstatus))
