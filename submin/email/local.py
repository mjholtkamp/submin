import os
from submin.models.exceptions import SendEmailError

binary = '/usr/sbin/sendmail'

def send(sender, receiver, message):
	p = os.popen("%s -t" % (binary), 'w')
	p.write(message)
	exitcode = p.close()
	if exitcode:
		raise SendEmailError

def might_work(sender, receiver):
	if os.path.exists(binary):
		return True
	raise SendEmailError('Local send mail: executable %s does not exist' %
			(binary, ))
