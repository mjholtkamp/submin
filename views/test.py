from dispatch.response import Response

class Test(object):
	def handler(self, req, path):
		return Response('Boeh! :)')