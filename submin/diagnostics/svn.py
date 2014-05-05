from submin.models import options
from submin.models.exceptions import UnknownKeyError

from .common import apache_modules, ApacheCtlError

def diagnostics():
	results = {}
	results['enabled_svn'] = 'svn' in options.value('vcs_plugins', '')

	if not results['enabled_svn']:
		results['svn_all'] = False
		return results

	try:
		svn_dir = options.env_path('svn_dir')
	except UnknownKeyError:
		results['svn_dir_set'] = False
	else:
		results['svn_dir_set'] = True

	found_mods = {}
	amods = []
	required_mods = ['dav', 'dav_svn', 'authz_svn', 'authn_dbd', 'dbd']
	try:
		amods = apache_modules()
	except ApacheCtlError as e:
		results['svn_apache_modules_err'] = True
		results['svn_apache_modules_errmsg'] = str(e)

	for mod in required_mods:
		found_mods.update({mod: mod in amods})

	all_mods_loaded = False not in found_mods.values()

	results['svn_apache_modules'] = found_mods
	results['svn_all'] = False not in results.values() and all_mods_loaded
	
	return results
