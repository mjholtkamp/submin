import re

from submin.models import options
from submin.email import smtp, local
from submin.models.exceptions import UnknownKeyError, SendEmailError
from .common import add_labels

fails = ['email_commit_sane', 'email_from_sane']
warnings = ['email_commit_set', 'email_from_set',
		'email_might_work_smtp_from']

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

	all_options = [x[0] for x in options.options()]
	sender = smtp_from
	if not results['email_from_set']:
		sender = 'root@localhost'

	sender = re.sub('.*<(.*)>.*', '\\1', sender)

	if 'smtp_hostname' in all_options:
		try:
			smtp.might_work(sender, 'nonexistent@example.net')
		except SendEmailError, e:
			results['email_might_work_smtp_from'] = False
			results['email_might_work_smtp_from_msg'] = str(e)
		else:
			results['email_might_work_smtp_from'] = True
	else:
		try:
			local.might_work(sender, 'nonexistent@example.net')
		except SendEmailError, e:
			results['email_might_work_smtp_from'] = False
			results['email_might_work_smtp_from_msg'] = str(e)
		else:
			results['email_might_work_smtp_from'] = True

	return add_labels(results, 'email_all', warnings, fails)
