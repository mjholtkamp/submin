import os
import re
import socket

from submin.dispatch.response import Response, Redirect
from submin.views.error import ErrorResponse
from submin.models import options
from submin.models.exceptions import UnknownKeyError

class Unauthorized(Exception):
	pass

def login_required(fun):
	login_url = options.url_path('base_url_submin') + 'login'

	def _decorator(self, *args, **kwargs):
		if 'user' not in self.request.session:
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

def generate_acl_list():
	"""A helper function for the decorator
	set a sane default, loopback IP's and the IP addresses that
	are used for the web server address. If this is not enough,
	the user should set the IP-address (see diagnostics).
	Since this might resolve, only use it when necessary.
	"""
	acls = ['127.0.0.1', '::1']
	vhost = options.value('http_vhost', 'localhost')
	netloc = vhost.replace('https://', '').replace('http://', '').strip('/')
	m = re.search('\[([0-9a-fA-F:]+)\]', netloc)
	if not m:
		m = re.search('^([^:]+)', netloc)

	if not m:
		return set(acls)

	hostname = m.group(1)

	# get IPv4 and IPv6 addresses
	try:
		acls.extend([x[4][0] for x in socket.getaddrinfo(hostname, 0)])
	except socket.gaierror as e:
		pass

	return set(acls)

def acl_required(acl_name):
	def _decorator(fun):
		try:
			acls = options.value(acl_name)
		except UnknownKeyError as e:
			acls = generate_acl_list()
		else:
			acls = [x.strip() for x in acls.split(',')]

		def _wrapper(self, *args, **kwargs):
			address = self.request.remote_address
			if address not in acls:
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
		if 'upgrade_user' not in self.request.session:
			if 'user' in self.request.session:
				return Redirect(main_url, self.request)

			return Redirect(login_url, self.request)

		return fun(self, *args, **kwargs)
	return _decorator
