import os
from submin.dispatch.response import Response, Redirect
from submin.views.error import ErrorResponse
from submin.models import options

class Unauthorized(Exception):
	pass

def login_required(fun):
	login_url = options.url_path('base_url_submin') + 'login'

	def _decorator(self, *args, **kwargs):
		if not 'user' in self.request.session:
			return Redirect(login_url, self.request)

		if not self.request.session['user']['is_authenticated']:
			return Redirect(login_url, self.request)

		return fun(self, *args, **kwargs)

	return _decorator

def admin_required(fun):
	@login_required
	def _decorator(self, *args, **kwargs):
		if not self.request.session['user']['is_admin']:
			raise Unauthorized("Admin privileges are required.")
		return fun(self, *args, **kwargs)
	return _decorator

def acl_required(acl_name):
	def _decorator(fun):
		acl = options.value(acl_name, '127.0.0.1, ::1').split(',')
		acl = [x.strip() for x in acl]
		def _wrapper(self, *args, **kwargs):
			address = self.request.remote_address
			if not address in acl:
				raise Unauthorized(
					"Your IP address [%s] does not have access" % address)
			return fun(self, *args, **kwargs)
		return _wrapper
	return _decorator

def upgrade_user_required(fun):
	"""Test if the upgrade_user is set (by the login view), otherwise
	redirect to login, or if the user is logged in, redirect to main url"""
	login_url = options.url_path('base_url_submin') + 'login'
	main_url = options.url_path('base_url_submin')

	def _decorator(self, *args, **kwargs):
		if not 'upgrade_user' in self.request.session:
			if 'user' in self.request.session:
				return Redirect(main_url, self.request)

			return Redirect(login_url, self.request)

		return fun(self, *args, **kwargs)
	return _decorator
