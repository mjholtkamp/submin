from dispatch.view import View
from template.shortcuts import evaluate_main
from dispatch.response import Response
from dispatch.response import HTTP500
from config.config import Config
from models.user import User
from models.group import Group
from auth.decorators import *

class Users(View):
	@login_required
	def handler(self, req, path):
		if req.is_ajax():
			return self.ajaxhandler(req, path)

		config = Config()

		localvars = {}

		try:
			user = User(path[0])
		except (IndexError, User.DoesNotExist):
			return Response('Woops, user does not exist!')

		localvars['user'] = user
		formatted = evaluate_main('users', localvars)
		return Response(formatted)
	handler = login_required(handler)

	def ajaxhandler(self, req, path):
		config = Config()

		success = False
		error = ''
		response = None
		username = ''

		if len(path) > 0:
			username = path[0]

		user = User(username)

		try:
			email = req.get.get('email')
			config.authz.setUserProp(username, 'email', email)
			success = True
		except Exception, e:
			error = 'Could not change email of user ' + username

		try:
			password = req.get.get('password')
			config.htpasswd.change(username, password)
			config.htpasswd.flush()
			success = True
		except Exception, e:
			error = 'Could not change password of user ' + username

		if success:
			response = Response('Success!')
		else:
			response = HTTP500(error)

		return response
