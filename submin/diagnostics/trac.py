from submin.models import options
from submin.models import trac
from submin.models.exceptions import UnknownKeyError

def diagnostics():
	results = {}
	results['enabled_trac'] = options.value('enabled_trac', 'no') != 'no'
	results['installed_trac'] = trac.tracAdminExists()

	# don't check for existence, submin creates it as needed
	try:
		trac_dir = options.env_path('trac_dir')
	except UnknownKeyError:
		results['trac_dir_set'] = False
	else:
		results['trac_dir_set'] = True

	results['trac_all'] = False not in results.values()
	
	return results
