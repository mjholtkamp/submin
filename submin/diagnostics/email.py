import re

from submin.models import options
from submin.email import fallback
from submin.models.exceptions import UnknownKeyError

def diagnostics():
	results = {}
	commit_email_from = options.value('commit_email_from', '')
	results['email_commit_set'] = commit_email_from != ''
	match = re.match('(.+) (<[^@>]+@[^@>]+\.[^@>]+>)', commit_email_from)
	results['email_commit_sane'] = match != None
	smtp_from = options.value('smtp_from', '')
	results['email_from_set'] = smtp_from != ''
	match = re.match('(.+) (<[^@>]+@[^@>]+\.[^@>]+>)', commit_email_from)
	results['email_from_sane'] = match != None

	results['email_all'] = False not in results.values()
	
	return results
