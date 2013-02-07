from submin.dispatch.view import View
from submin.dispatch.response import FileResponse, TeapotResponse
from submin.models import options
import os

class PassThrough(View):
	"""Make sure this class isn't actaully used!
	This is a very inefficient way to handle requests, it's better
	to let a webserver serve the static files. However, for
	development and testing it is fine.
	"""
	def handler(self, req, path):
		"""The subdir is expected to be in self.custom"""
		wwwroot = options.static_path('www')
		fullpath = wwwroot + self.custom + '/'.join(path)
		canonicalpath = os.path.realpath(fullpath)

		# Someone is trying to be funny? We can be funny too!
		if not canonicalpath.startswith(wwwroot):
			return TeapotResponse("You tried to brew coffee, but I'm a teapot!")

		_, ext = os.path.splitext(fullpath)
		
		return FileResponse(''.join(file(fullpath).readlines()), self.mimetype(ext))

	def mimetype(self, ext):
		mimetypes = {
			'.png': 'image/png',
			'.css': 'text/css',
			'.js': 'application/javascript',
		}
		if ext in mimetypes:
			return mimetypes[ext]

		return 'application/octet-stream'
