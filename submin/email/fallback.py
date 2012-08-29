import local
import smtp
from submin.models.exceptions import SendEmailError

def sendmail(sender, receiver, message):
	msg_e = message.encode('utf-8')
	try:
		smtp.send(sender, receiver, msg_e)
	except SendEmailError:
		# this can still raise SendEmailError
		local.send(sender, receiver, msg_e)
