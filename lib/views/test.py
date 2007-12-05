from dispatch.view import View
from dispatch.response import Response

class Test(View):
	def handler(self, req, path, ajax=False):
		if ajax:
			return Response('Booh from an ajax-request!')
		counter = req.session.get('counter', 0)
		counter += 1
		req.session['counter'] = counter
		return Response('visit #' + str(counter))
		return Response('Boeh! :)')
