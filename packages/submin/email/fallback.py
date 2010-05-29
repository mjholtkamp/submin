import local
import smtp
from submin.models.exceptions import SendEmailError

def sendmail(sender, receiver, message):
	try:
		smtp.send(sender, receiver, message)
	except SendEmailError:
		# this can still raise SendEmailError
		local.send(sender, receiver, message)