import os

from submin.dispatch.view import View
from submin.dispatch.response import Response, Redirect
from submin.views.error import ErrorResponse
from submin.template.shortcuts import evaluate
from submin.models.exceptions import NoMD5PasswordError, UnknownUserError
from submin.models import user
from submin.models import options
from submin.models.storage import database_isuptodate

class Login(View):
	def handler(self, request, path):
		if 'auto_authenticate' in request.session:
			username = request.session['auto_authenticate']
		else:
			if not request.post:
				return self.evaluate_form(session=request.session)
			username = request.post.get('username', '')
			password = request.post.get('password', '')

		invalid_login = True
		u = None
		try:
			u = user.User(username)
			invalid_login = False
		except UnknownUserError as e:
			pass

		if 'auto_authenticate' in request.session:
			del request.session['auto_authenticate']
			request.session['change_password_hint'] = True
		else:
			try:
				if not u or not u.check_password(password):
					return self.evaluate_form('Not a valid username and password combination')
			except NoMD5PasswordError as e:
				return self.evaluate_form(str(e))

			if invalid_login:
				return self.evaluate_form('Not a valid username and password combination')

		if not database_isuptodate():
			localvalues = {}
			request.session['upgrade_user'] = True
			base_url = options.url_path('base_url_submin')
			localvalues['base_url'] = str(base_url)
			localvalues['session_user'] = u
			return Response(evaluate('database_upgrade.html', localvalues))

		url = options.url_path('base_url_submin')
		if 'redirected_from' in request.session:
			login_url = options.url_path('base_url_submin') + 'login'
			url = request.session['redirected_from']
			if url.startswith(login_url):
				url = options.url_path('base_url_submin')

		session_user = u.session_object()
		session_user['is_authenticated'] = True
		request.session['user'] = session_user
		request.session.cleanup()

		return Redirect(url, request, store_url=False)


	def evaluate_form(self, msg='', session=None):
		localvalues = {}
		localvalues['msg'] = msg
		localvalues['base_url'] = options.url_path('base_url_submin')
		if session and 'user' in session and 'is_authenticated' in session['user']:
			if session['user']['is_authenticated']:
				localvalues['is_authenticated'] = True
				localvalues['username'] = session['user']['name']

		return Response(evaluate('login.html', localvalues))

class Password(View):
	def handler(self, req, path):
		if req.is_ajax():
			return Response('Invalid')

		if len(path) > 0:
			username = path[0]
			if len(path) > 1:
				key = path[1]

			return self.reset_password(req, username, key)
		return self.send_email(req, path)

	def reset_password(self, req, username, key):
		templatevars = { 'base_url': options.url_path('base_url_submin') }
		if 'auto_authenticate' in req.session:
			del req.session['auto_authenticate']

		try:
			u = user.User(username)
		except UnknownUserError:
			raise

		if not u.valid_password_reset_key(key):
			templatevars['invalid'] = True
		else:
			templatevars['reset'] = True
			req.session['auto_authenticate'] = username
			u.clear_password_reset_key()

		formatted = evaluate('password.html', templatevars)
		return Response(formatted)

	def send_email(self, req, path):
		templatevars = { 'base_url': options.url_path('base_url_submin') }
		username = req.post.get('username', '')
		if username:
			try:
				u = user.User(username)
				u.prepare_password_reset(req.remote_address)
				templatevars['sent'] = True
			except UnknownUserError:
				templatevars['sent'] = True
		else:
			templatevars['form'] = True

		formatted = evaluate('password.html', templatevars)
		return Response(formatted)

class Logout(View):
	def handler(self, request, path):
		if 'user' in request.session:
			request.session['user']['is_authenticated'] = False
		request.session.clear()
		url = options.url_path('base_url_submin')
		return Redirect(url, request)

