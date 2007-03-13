import re
import os
from lib.utils import mimport
mod_htpasswd = mimport('lib.htpasswd')

admin = True
login_required = True

def printpage(input):
	print '''
	<form name="" action="%srepository" method="post">
	<div class="container">
		<div class="row">
			<label for="name">New repository name:</label>
			<input class="form" type="text" name="name" value="" id="name" />
		</div>
		<div class="row">
			<label>&nbsp;</label>
			<input class="form" type="submit" value="add" />
		</div>
	</div>
	</form>
	''' % input.base

def handleinput(input):
	if input.post.has_key('name'):
		addrepository(input)
		print

	printpage(input)

def _getrepositories(input):
	import ConfigParser
	try:
		reposdir = input.config.get('svn', 'repositories')
	except ConfigParser.NoSectionError, e:
		raise "Error in configuration. No repositories option in svn section."

	return reposdir

def addrepository(input):
	name = input.post['name']
	p = re.compile('[^a-zA-Z0-9+]')
	if p.search(name):
		print 'illegal characters found, not adding'
		return

	repos = _getrepositories(input)

	path = os.path.join(repos, name)

	if os.access(path, os.F_OK):
		print 'repository %s already exists' % name
		return

	if os.system('svnadmin create %s' % path) == 0:
		print 'repository %s created' % name
	else:
		print 'couldn\'t create repository %s, sorry!' % name

def handler(input):
	print input.html.header('repository')

	handleinput(input)

	print input.html.footer()
