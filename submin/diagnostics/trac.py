import os
import urllib2
import socket # for urllib timeout
import xml.etree.ElementTree as ET

from submin.auth.decorators import generate_acl_list
from submin.path.path import Path
from submin.models import options
from submin.models import trac
from submin.models.exceptions import UnknownKeyError

class SyncError(Exception):
	pass

def diagnostics():
	results = {}
	results['enabled_trac'] = options.value('enabled_trac', 'no') != 'no'

	if not results['enabled_trac']:
		results['trac_all'] = False
		return results

	results['installed_trac'] = trac.tracAdminExists()

	results['trac_acl_hook'] = options.value('acl_hook', '') != ''
	results['trac_acl_hook_recommendation'] = ', '.join(generate_acl_list())
	results['trac_sync_access'] = True
	try:
		have_trac_sync_access()
	except SyncError, e:
		results['trac_sync_access'] = False
		results['trac_sync_access_msg' ] = str(e)

	# don't check for existence, submin creates it as needed
	try:
		trac_dir = options.env_path('trac_dir')
	except UnknownKeyError:
		results['trac_dir_set'] = False
	else:
		results['trac_dir_set'] = True

	try:
		htpasswd_file = options.env_path("htpasswd_file")
		results['trac_htpasswd_file'] = htpasswd_file
		results['trac_htpasswd_dir_exists'] = os.path.exists(htpasswd_file.dirname())
		results['trac_htpasswd_dir'] = htpasswd_file.dirname()
	except UnknownKeyError:
		results['trac_htpasswd_file'] = ""

	results['trac_all'] = False not in results.values()
	
	return results

def have_trac_sync_access():
	baseurl = Path(options.http_vhost() + options.url_path('base_url_submin'))
	# because we don't specify a full path, this will never succeed, but
	# it will set the 'inacl' attribute to True/False
	joburl = str(baseurl + 'hooks' + 'trac-sync')

	try:
		response = urllib2.urlopen(joburl, timeout=5)
	except urllib2.HTTPError, e:
		raise SyncError('HTTP error: %s' % str(e))
	except urllib2.URLError, e:
		raise SyncError('URL invalid %u: %s' % (e.reason[0], e.reason[1]))
	except socket.timeout, e:
		raise SyncError('Timeout: are we running a single-threaded server?')

	root = ET.fromstring(response.read())
	command = root.find('./command')
	if not command:
		raise SyncError(root)

	if 'inacl' not in command.attrib or command.attrib['inacl'].lower() == 'false':
		msgnodes = root.findall('./command/errormsgs/msg')
		raise SyncError('\n'.join([x.text for x in msgnodes]))
