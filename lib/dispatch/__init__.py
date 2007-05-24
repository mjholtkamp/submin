from dispatch.response import Response, HTTP404

from views.test import Test
from views.usergroups import UserGroups

classes = {
	'test': Test(),
	'usergroups': UserGroups(),
}

def dispatcher(request):
	path = request.path_info.strip('/').split('/')
	
	handlerName = 'handler'
	ajax = False
	if path[0].lower() == 'ajax':
		ajax = True
		del path[0]
	
	if path[0].lower() in classes:
		cls = classes[path[0].lower()]
		if not hasattr(cls, handlerName):
			raise Exception, "No handler %r found for view %r" % (handlerName, path[0].lower())
		
		del path[0]
		handler = getattr(cls, handlerName)
		try:
			response = handler(request, path, ajax=ajax)
		except TypeError, e:
			if str(e).strip() != "handler() got an unexpected keyword argument 'ajax'":
				raise
			response = handler(request, path)
		
		if not issubclass(response.__class__, Response):
			raise Exception, "Handler %r should return a Response instance" % handler
		
	else:
		response = HTTP404()

	request.status(response.status_code)
	request.setHeaders(response.headers)
	request.writeHeaders()
	request.write(response.content)

