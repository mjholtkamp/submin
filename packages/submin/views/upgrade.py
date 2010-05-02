from submin.template.shortcuts import evaluate
from submin.dispatch.response import Response
from submin.dispatch.view import View
from submin.auth.decorators import *
from submin.models.storage import database_isuptodate, database_evolve

class Upgrade(View):
	@upgrade_user_required
	def handler(self, req, path):
		localvars = {}
		localvars['uptodated'] = True
		localvars['base_url'] = options.value('base_url_submin')
		
		if database_isuptodate():
			localvars['alreadyuptodate'] = True
		else:
			database_evolve()
			localvars['alreadyuptodate'] = False

		formatted = evaluate('database_upgrade.html', localvars)

		return Response(formatted)
