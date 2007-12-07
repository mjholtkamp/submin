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

		username = ''

		if len(path) > 0:
			username = path[0]

		user = User(username)

		if 'email' in req.get:
			return self.setEmail(req, user)

		if 'password' in req.get:
			return self.setPassword(req, user)

		return HTTP500('You tried to submit an empty field value')

	def setEmail(self, req, user):
		try:
			user.email = req.get.get('email')
			return Response('Success!')
		except Exception, e:
			return HTTP500('Could not change email of user ' + user.name)

	def setPassword(self, req, user):
		try:
			user.password = req.get.get('password')
			return Response('Success!')
		except Exception, e:
			return HTTP500('Could not change password of user ' + user.name)
