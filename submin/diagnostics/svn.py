from submin.models import options
from submin.models.exceptions import UnknownKeyError

from common import apache_modules

def diagnostics():
	results = {}
	results['enabled_svn'] = 'svn' in options.value('vcs_plugins', '')

	try:
		svn_dir = options.env_path('svn_dir')
	except UnknownKeyError:
		results['svn_dir_set'] = False
	else:
		results['svn_dir_set'] = True

	amods = apache_modules()

	required_mods = ['dav_module', 'dav_svn_module', 'authz_svn_module', 'authn_dbd_module']
	found_mods = {}
	for mod in required_mods:
		found_mods.update({mod: mod in amods})

	all_mods_loaded = False not in found_mods.values()

	results['svn_apache_modules'] = found_mods
	results['svn_all'] = False not in results.values() and all_mods_loaded
	
	return results
