from template.shortcuts import evaluate_main
from dispatch.response import Response
from config.config import Config
from models.user import User
from models.group import Group

class Users(object):
	def handler(self, req, path, ajax=False):
		if ajax:
			return self.ajaxhandler(req, path)

		config = Config()

		localvars = {}

		try:
			user = User(config, path[0])
		except (IndexError, User.DoesNotExist):
			return Response('Woops, user does not exist!') 


		localvars['user'] = user
		formatted = evaluate_main('users', localvars)
		return Response(formatted)

	def ajaxhandler(self, req, path):
		config = Config()

		success = False
		error = ''

		username = path[0]

		try:
			email = req.get.get('email')
			config.authz.setUserProp(username, 'email', email)
			success = True
		except Exception, e:
			error = 'Could not change email of user ' + username

		try:
			password = req.get.get('password')
			htpasswd = HTPasswd(config.get('svn', 'access_file'))
			htpasswd.change(username, password)
			htpasswd.flush()
			success = True
		except Exception, e:
			error = 'Could not change password of user ' + username

		if success:
			error = 'Success!'

		return Response(error)
