import os
from config.config import Config
from dispatch.response import Response, Redirect
from views.error import ErrorResponse

class Unauthorized(Exception):
	pass

def login_required(fun):
	config = Config()
	login_url = os.path.join(config.get('www', 'media_url'), 'login')

	def _decorator(self, *args, **kwargs):
		if not self.request.is_ajax():
			self.request.session['redirected_from'] = self.request.url

		if not 'user' in self.request.session:
			return Redirect(login_url)

		if not self.request.session['user'].is_authenticated:
			return Redirect(login_url)

		return fun(self, *args, **kwargs)

	return _decorator

def admin_required(fun):
	@login_required
	def _decorator(self, *args, **kwargs):
		if not self.request.session['user'].is_admin:
			raise Unauthorized("Submin-admin privileges are required.")
		return fun(self, *args, **kwargs)
	return _decorator
