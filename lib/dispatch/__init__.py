from dispatch.response import Response, HTTP404, XMLStatusResponse

from config.config import Config

from views.error import ErrorResponse
from views.test import Test
from views.users import Users
from views.groups import Groups
from views.authviews import Login, Logout
from views.repositories import Repositories
from views.intro import Intro

from dispatch.session import Session

classes = {
	'test': Test,
	'users': Users,
	'groups': Groups,
	'login': Login,
	'logout': Logout,
	'repositories': Repositories,
	'': Intro,
}

def init_tests():
	"""Initialize url-coupling to test-views
	Only loaded if config-options in section "tests" are present
	"""
	config = Config()
	if not config.cp.has_section("tests"):
		return
	from views.uiscenarios import UIScenarios
	classes["uiscenarios"] = UIScenarios

init_tests()

def dispatcher(request):
	# Add session information to request
	request.session = Session(request)

	path = request.path_info.strip('/').split('/')

	handlerName = 'handler'
	if path[0].lower() in classes:
		cls = classes[path[0].lower()](request)
		if not hasattr(cls, handlerName):
			raise Exception, "No handler %r found for view %r" % (handlerName, path[0].lower())

		del path[0]
		handler = getattr(cls, handlerName)
		try:
			response = handler(request, path)

			if not issubclass(response.__class__, Response):
				raise Exception, "Handler %r should return a Response instance" % handler
		except Exception, e:
			import traceback
			import sys
			trace = traceback.extract_tb(sys.exc_info()[2])
			list = traceback.format_list(trace)
			list = '<br />\n'.join(list)

			if not request.is_ajax():
				response = ErrorResponse(str(e), request=request, details=list)
			else:
				response = XMLStatusResponse(False, str(e))

	else:
		response = HTTP404('/'.join(path))

	response.setCookieHeaders(request.cookieHeaders())

	return response

