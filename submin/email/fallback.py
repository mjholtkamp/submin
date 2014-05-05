from submin.models.exceptions import SendEmailError

from . import local
from . import smtp

def sendmail(sender, receiver, message):
	msg_e = message.encode('utf-8')
	try:
		smtp.send(sender, receiver, msg_e)
	except SendEmailError:
		# this can still raise SendEmailError
		local.send(sender, receiver, msg_e)
