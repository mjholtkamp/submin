import os
from config.config import Config
from dispatch.response import Response, Redirect

def login_required(fun):
	config = Config()
	login_url = os.path.join(config.get('www', 'media_url'), '/login')

	def _decorator(self, *args, **kwargs):
		if 'ajax' not in self.request.get and 'ajax' not in self.request.post:
			self.request.session['redirected_from'] = self.request.url

		if not 'user' in self.request.session:
			return Redirect(login_url)

		if not self.request.session['user'].is_authenticated:
			return Redirect(login_url)

		return fun(self, *args, **kwargs)
	
	return _decorator
