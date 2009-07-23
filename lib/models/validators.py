import re

# regex for quick email check. No quotes allowed, be very allowing
# for domain-names and ip-addresses.
EMAIL_REGEX = re.compile('^[^\'"@]+@(([\w-]\.?)+)$')

# Usernames can not contain newlines or quotes (due to restrictions in authz)
USERNAME_REGEX = re.compile('[\n\'"]')

# regex for quick fullname check. No quotes or newlines allowed.
FULLNAME_REGEX = re.compile('[\'"\n]')

class InvalidEmail(Exception):
	def __init__(self, email):
		Exception.__init__(self, "Invalid email: %s" % email)

class InvalidUsername(Exception):
	def __init__(self, username):
		Exception.__init__(self,
				"Invalid characters found in user name: %s" % username)

class InvalidFullname(Exception):
	def __init__(self, fullname):
		Exception.__init__(self,
				"Invalid characters found in full name: %s" % fullname)

def validate_email(email):
	return EMAIL_REGEX.match(email)

def validate_username(user):
	return not USERNAME_REGEX.search(user):

def validate_fullname(fullname):
	return not FULLNAME_REGEX.search(fullname):
