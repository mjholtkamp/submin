from submin.models import options
from submin.models.exceptions import UnknownKeyError, SendEmailError
from smtplib import SMTP, SMTPException
import socket

def send(sender, receiver, message):
	server = options.value("smtp_hostname", "localhost")
	port = options.value("smtp_port", 25)
	username = options.value("smtp_username", "")
	password = options.value("smtp_password", "")

	try:
		server = SMTP(server, int(port))
		if username != "" and password != "":
			server.login(username, password)

		server.sendmail(sender, [receiver], message)
		server.quit()
	except (SMTPException, socket.error), e:
		raise SendEmailError(str(e))
