import os
from submin.models.exceptions import SendEmailError

def send(sender, receiver, message):
	binary = '/usr/sbin/sendmail'
	p = os.popen("%s -t" % (binary), 'w')
	p.write(message)
	exitcode = p.close()
	if exitcode:
		raise SendEmailError