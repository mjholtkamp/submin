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
			# The .login() function only accepts str, not unicode, so force it
			server.login(str(username), str(password))

		server.sendmail(sender, [receiver], message)
		server.quit()
	except (SMTPException, socket.error) as e:
		raise SendEmailError(str(e))

def might_work(sender, receiver):
	server = options.value("smtp_hostname", "localhost")
	port = options.value("smtp_port", 25)
	username = options.value("smtp_username", "")
	password = options.value("smtp_password", "")
	my_hostname = socket.getfqdn()

	test_commands = [
		('EHLO', my_hostname),
		('MAIL FROM:', sender),
		('RCPT TO:', receiver)
	]

	try:
		server = SMTP(server, int(port))
		if username != "" and password != "":
			# The .login() function only accepts str, not unicode, so force it
			server.login(str(username), str(password))

		for cmd, arg in test_commands:
			code, msg = server.docmd(cmd, arg)
			if code == 250:
				continue

			raise SendEmailError('SMTP: %s was not accepted: %s' % (cmd, msg))

		# do not actually send something
		server.quit()
	except (SMTPException, socket.error) as e:
		raise SendEmailError('SMTP: %s' % (str(e), ))
