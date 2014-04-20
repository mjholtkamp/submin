import os
import urllib2
import socket # for urllib timeout
import xml.etree.ElementTree as ET
import ConfigParser

from submin.auth.decorators import generate_acl_list
from submin.path.path import Path
from submin.models import options
from submin.models import trac
from submin.models.repository import Repository, DoesNotExistError
from submin.models.exceptions import UnknownKeyError

class SyncError(Exception):
	pass

def diagnostics():
	results = {}
	results['enabled_trac'] = options.value('enabled_trac', 'no') != 'no'

	if not results['enabled_trac']:
		results['trac_all'] = False
		return results

	results['installed_trac'] = trac.has_trac_admin()

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

		envs = list(missing_config_envs(trac_dir))

		missing_config = [(x[0], x[2]) for x in envs if x[1]]
		results['trac_envs_missing_config'] = missing_config
		results['trac_envs_complete'] = 0 == len(missing_config)

		orphaned = [x[0] for x in envs if not x[1]]
		results['trac_envs_orphaned'] = orphaned
		results['trac_envs_all_connected'] = 0 == len(orphaned)

	try:
		htpasswd_file = options.env_path("htpasswd_file")
		results['trac_htpasswd_file'] = htpasswd_file
		results['trac_htpasswd_dir_exists'] = os.path.exists(htpasswd_file.dirname())
		results['trac_htpasswd_dir'] = htpasswd_file.dirname()
	except UnknownKeyError:
		results['trac_htpasswd_file'] = ""

	results['trac_base_url'] = options.url_path('base_url_trac')
	results['trac_all'] = False not in results.values()
	
	return results

def have_trac_sync_access():
	baseurl = Path(options.http_vhost() + options.url_path('base_url_submin'))
	# because we don't specify a full path, this will never succeed, but
	# it will set the 'inacl' attribute to True/False
	joburl = str(baseurl + 'hooks' + 'trac-sync')

	try:
		response = urllib2.urlopen(joburl, timeout=2)
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

def has_option(config, section, option, value):
	"""Check if ConfigParser object *config* has option
	This will resolve wildcards if necessary. For example, if the option
	tracopt.versioncontrol.git.git_fs.gitconnector is not found, also try:
	tracopt.versioncontrol.git.git_fs.*
	tracopt.versioncontrol.git.*
	tracopt.versioncontrol.*
	tracopt.*
	Because they will match as well. WARNING: we assume Trac will pick the
	most specific option.
	"""
	while True:
		try:
			return config.get(section, option) == value
		except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
			if option.endswith('.*'):
				option = option[:-2]

			if not '.' in option:
				return False

			option = option[:option.rindex('.')] + '.*'
			continue

def missing_config_envs(trac_dir):
	"""Yields trac_envs that are 1) orphaned or 2) have missing configs
	Orphaned means that there is a trac environment, but no git/svn repository
	Missing configs means that there are some configs missing that Submin
	recommends.
	Each trav_env is a tuple of:
	   (trac_name, connected, missing_options)

	If 'connected' is False, then it is orphaned.

	missing_options is a dict of {section: [missing_option, ...], ...}
	"""
	trac_envs = []
	trac_sync_components = [
		'tracopt.ticket.commit_updater.committicketreferencemacro',
		'tracopt.ticket.commit_updater.committicketupdater',
	]
	# trac components to enable for each vcs type
	trac_vcs_components = {
		'git': [
			'tracopt.versioncontrol.git.git_fs.csetpropertyrenderer',
			'tracopt.versioncontrol.git.git_fs.gitconnector',
			'tracopt.versioncontrol.git.git_fs.gitwebprojectsrepositoryprovider'
		],
		'svn': [
			'tracopt.versioncontrol.svn.svn_fs.subversionconnector',
			'tracopt.versioncontrol.svn.svn_prop.subversionmergepropertydiffrenderer',
			'tracopt.versioncontrol.svn.svn_prop.subversionmergepropertyrenderer',
			'tracopt.versioncontrol.svn.svn_prop.subversionpropertyrenderer'
		]
	}

	# per vcs, for each section, list of:
	# (option, expected_value, fatal_if_different)
	other_options = {
		'git': {
			'ticket': [('commit_ticket_update_check_perms', 'false', False)]
		}
	}

	for root, dirs, files in os.walk(trac_dir):
		for d in dirs:
			if d not in ['.', '..']:
				trac_envs.append(d)
		break

	for trac_env in sorted(trac_envs):
		# We would like to use: trac-admin <env> config get <section> <option>
		# but this does not resolve wildcards and is inefficient (lots of
		# process spawning; one for each option in each repository, also
		# parsing might pose a proble, unless exit codes are honered (didn't
		# check)).
		# So instead, we use ConfigParser to read the ini file and check
		# each option and their wildcards.
		fullpath = os.path.join(trac_dir, trac_env, 'conf', 'trac.ini')
		config = ConfigParser.RawConfigParser()
		config.read(fullpath)

		connected = False
		missing_options = {}
		components = []

		reposdir = config.get('trac', 'repository_dir')
		repostype = config.get('trac', 'repository_type')
		try:
			repos = Repository(trac_env, repostype)
		except DoesNotExistError, e:
			pass
		else:
			connected = True

			if repos.tracCommitHookEnabled():
				components.extend(trac_sync_components)

		components.extend(trac_vcs_components[repostype])

		all_options = {}
		if repostype in other_options:
			all_options.update(other_options[repostype])
		all_options['components'] = [(x, 'enabled', True) for x in components]

		for section, option_values in all_options.iteritems():
			for option, value, fatal in option_values:
				if not has_option(config, section, option, value):
					if not section in missing_options:
						missing_options[section] = []
					missing_options[section].append((option, value, fatal))

		if len(missing_options) > 0 or not connected:
			yield (trac_env, connected, missing_options)

	return
