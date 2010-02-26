import os
from submin.dispatch.response import Response, Redirect
from submin.views.error import ErrorResponse
from submin.models import options

class Unauthorized(Exception):
	pass

def login_required(fun):
	login_url = os.path.join(str(options.env_path('base_url_submin')), 'login')

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
			raise Unauthorized("Admin privileges are required.")
		return fun(self, *args, **kwargs)
	return _decorator
