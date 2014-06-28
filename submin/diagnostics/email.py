import re

from submin.models import options
from submin.email import fallback
from submin.models.exceptions import UnknownKeyError
from .common import add_labels

fails = ['email_commit_sane', 'email_from_sane']
warnings = ['email_commit_set', 'email_from_set']

def diagnostics():
	results = {}
	commit_email_from = options.value('commit_email_from', '')
	results['email_commit_set'] = commit_email_from != ''
	match = re.match('(.+) (<[^@>]+@[^@>]+\.[^@>]+>)', commit_email_from)
	results['email_commit_sane'] = match != None
	results['email_commit_current_value'] = commit_email_from
	smtp_from = options.value('smtp_from', '')
	results['email_from_set'] = smtp_from != ''
	match = re.match('(.+) (<[^@>]+@[^@>]+\.[^@>]+>)', smtp_from)
	results['email_from_sane'] = match != None
	results['email_from_current_value'] = smtp_from

	return add_labels(results, 'email_all', warnings, fails)
