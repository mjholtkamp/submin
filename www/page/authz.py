import urllib
from lib.utils import mimport
iif = mimport('lib.utils').iif
#html = mimport('lib.html')
exceptions = mimport('lib.exceptions')
mod_authz = mimport('lib.authz')

admin = False

def _getauthz(input):
	return input.authz

def _getrepositories(input):
	import ConfigParser
	try:
		reposdir = input.config.get('svn', 'repositories')
	except ConfigParser.NoSectionError, e:
		raise "Error in configuration. No repositories option in svn section."

	import glob, os.path
	_repositories = glob.glob(os.path.join(reposdir, '*'))
	repositories = []
	for repos in _repositories:
		if os.path.isdir(repos):
			repositories.append(repos[len(reposdir)+1:])
	return repositories

def _makeUrl(input, repos, path=None):
	import ConfigParser
	import os
	try:
		reposdir = input.config.get('svn', 'repositories')
	except ConfigParser.NoSectionError, e:
		raise "Error in configuration. No repositories option in svn section."

	url = 'file://' + reposdir
	url = os.path.join(url, repos)
	if path:
		url = os.path.join(url, path)
	return url

def _getPaths(repository):
	import pysvn

	client = pysvn.Client()
	
	files = client.ls(repository, recurse=True)
	dirs = []
	for file in files:
		if file['kind'] == pysvn.node_kind.dir:
			dirs.append(file['name'])

	return dirs

def _authzify(url, base, repository):
	index = len(base)
	path = url[index:]
	if not path.startswith('/'):
		path = '/' + path
	return repository + ':' + path

def _select(user, permission):
	checked = ' selected="selected"'
	select = '<select name="%s">' % user
	select += '\n\t\t\t<option value="-"%s>-</option>' % iif(permission == '', checked, '')
	select += '\n\t\t\t<option value="r"%s>r</option>' % iif(permission == 'r', checked, '')
	select += '\n\t\t\t<option value="rw"%s>rw</option>' % iif(permission == 'rw', checked, '')
	select += '\n\t\t</select>'
	return select

def handler(input):
	msg = None
	if input.get.has_key('msg'):
		msg = input.get['msg'][-1]

	authz = _getauthz(input)

	print input.html.header('Permissions')

	if msg:
		print '<p class="msg">%s</p>' % msg

	print '<h2>Permissions</h2>'
	print '<p><a href="%s/authz/addpath">Add path</a> <small>(using a path-browser)</small></p>' % input.base
	print '''<form action="authz/manualaddpath" method="post">
		<p><small>Repository:</small> <input type="text" name="repos" />
		   <small>Path:</small> <input type="text" name="path" />
		   <input type="submit" value="Manually add a path" /></p>
	</form>'''

	print '<table style="border-collapse: collapse">'
	print '\t<thead>'
	print '\t\t<td></td>'
	print '\t\t<th style="width: 150px" align="left">user / group</th>'
	print '\t\t<th align="left">Permission</th>'
	print '\t</thead>'

	paths = authz.paths()
	paths.sort()
	for repos, path in paths:
		rpath = '%s%s' % (iif(repos, str(repos) + ':', ''), path)

		print '<form action="%s/authz/saveperm" method="post">' % input.base
		print '\t<input type="hidden" name="path" value="%s%s" />' % \
				(iif(repos is not None, str(repos) + ':', ''), 
				urllib.quote(path))
		print '\t<tr style="border-top: 1px solid #000">'
		print '\t\t<td></td>'
		print '\t\t<th align="left">%s%s</th>' % \
			(iif(repos, str(repos) + ':', ''), path)
		print '''\t\t<td>
		<a href="%s/authz/delpath?path=%s" onclick="return confirm('Do you really want to delete %s? (There is no undo)')" title="Delete">[X]</a>
		| <a href="%s/authz/addperm?path=%s" title="Add permission">[+]</a>
		</td>''' % \
				(input.base, urllib.quote(rpath), rpath, input.base, 
				urllib.quote(rpath))
		print '\t</tr>'
		permissions = authz.permissions(repos, path)
		permissions.sort()
		for user, permission in permissions:
			group = False
			if user.startswith('@'):
				try:
					members = authz.members(user[1:])
					group = True
				except mod_authz.UnknownGroupError:
					members = []
				members.sort()

			print '\t<tr>'
			print '\t\t<td><input type="checkbox" title="Delete this user from %s" name="del_%s" value="1" /></td>' % (rpath, user)

			if user.startswith('@'):
				print '\t\t<td><a href="group?group=%s" title="%s">%s</a></td>' %\
						(urllib.quote(user[1:]), ', '.join(members), user)
			else:
				print '\t\t<td>%s</td>' % user
			print '\t\t<td>%s</td>' % _select(user, permission)
			print '\t</tr>'
		print '\t<tr>'
		print '\t\t<td></td>'
		print '\t\t<td colspan="2" align="right">'
		print '\t\t\t<input type="submit" value="Save %s%s" />' %\
				(iif(repos is not None, str(repos) + ':', ''), path)
		print '\t\t</td>\n\t</tr>'
		print '</form>'
	print '</table>'

	print input.html.footer()


def saveperm(input):
	authz = _getauthz(input)
	repos = None
	path = input.post['path']
	if ':' in path:
		repos, path = path.split(':', 1)
	for key, value in input.post.iteritems():
		if key != 'path' and not key.startswith('del'):
			if value not in ('-', 'r', 'rw'):
				print 'Wrong permission:', value
				return
			if value == '-':
				value = ' '
			if 'del_%s' % key in input.post:
				continue
			authz.setPermission(repos, path, key, value)
		elif key.startswith('del'):
			authz.removePermission(repos, path, key[4:].strip())

	raise exceptions.Redirect, '%s/authz?msg=Permissions+saved' % input.base

def addperm(input):
	authz = _getauthz(input)
	if input.get.has_key('path'):
		path = input.get['path'][-1]
		print input.html.header('Adding permission to %s' % path)
		print '<h2>Adding permission to %s</h2>' % path
		print '''<form action="%s/authz/addperm" method="post" name="perm">
	<input type="hidden" name="path" value="%s" />
	<input type="text" name="member" /> %s <input type="submit" value="Add user" />
</form>''' % (input.base, path, _select('newuser', '-'))

		print '<h2>Groups <small>(For your adding convenience)</small>:</h2><ul>'
		groups = authz.groups()
		groups.sort()
		for group in groups:
			members = authz.members(group)
			members.sort()
			print '''
		<li><a href="#" onclick="document.perm.member.value='@%s'; return false" title="%s">%s</a></li>''' %\
				(group, ', '.join(members), group)
		print '</ul>'

		print input.html.footer()
	elif input.post.has_key('member'):
		repos = None
		path = input.post['path']
		if ':' in path:
			repos, path = path.split(':', 1)

		member = input.post['member']
		permission = input.post['newuser']
		if permission not in ('-', 'r', 'rw'):
			print 'Wrong permission:', value
			return
		if permission == '-':
			permission = ' '
		authz.setPermission(repos, path, member, permission)
		raise exceptions.Redirect, '%s/authz?msg=Permissions+added' % input.base

def delpath(input):
	authz = _getauthz(input)
	if input.get.has_key('path'):
		repos = None
		path = input.get['path'][-1]
		if ':' in path:
			repos, path = path.split(':', 1)
		authz.removePath(repos, path)
	raise exceptions.Redirect, '%s/authz?msg=Path+deleted' % input.base

def addpath(input):
	authz = _getauthz(input)
	repositories = _getrepositories(input)
	if not input.get.has_key('path'):
		print input.html.header('Adding path')
		print '<h2>Adding path</h2>'
		if input.get.has_key('msg'):
			print '<p class="msg">%s</p>' % input.get['msg'][0]

		print '<ul>'
		for repos in repositories:
			url = _makeUrl(input, repos)
			# root...
			authzroot = '%s:/' % repos
			if [None, '/'] not in authz.paths():
				print '<li><a href="authz/addpath?path=/">/</a></li>'

			print '<li><a href="authz/addpath?path=%s">%s</a>' % \
					(urllib.quote(authzroot), authzroot)
			# ... and other paths, via pysvn!
			paths = _getPaths(url)
			if paths:
				print '<ul>'
				for path in paths:
					authzpath = _authzify(path, url, repos)
					if authzpath not in authz.parser.sections():
						print '<li><a href="authz/addpath?path=%s">%s</a></li>' % \
								(urllib.quote(authzpath), authzpath)
				print '</ul>'
			print '</li>'
		print '</ul>'
		print input.html.footer()
	elif input.get.has_key('path'):
		# something with authz.addPath(repos, path)
		path = input.get['path'][0]
		repos = None
		if ':' in path:
			repos, path = path.split(':', 1)
		if [repos, path] not in authz.paths():
			authz.addPath(repos, path)
			raise exceptions.Redirect, '%s/authz?msg=Path+added' % input.base
		else:
			raise exceptions.Redirect, \
				'%s/authz/addpath?msg=Path+already+managed' % input.base

def manualaddpath(input):
	repos = input.post.get('repos', None)
	path = input.post.get('path', None)
	if not repos and path != '/':
		msg = urllib.quote("Please fill in both fields!")
		raise exceptions.Redirect, '%s/authz?msg=%s' % (input.base, msg)
	input.authz.addPath(repos, path)

	msg = urllib.quote("Path added")
	raise exceptions.Redirect, '%s/authz?msg=%s' % (input.base, msg)
		
