import re

# regex for quick email check. No quotes allowed, be very allowing
# for domain-names and ip-addresses.
EMAIL_REGEX = re.compile('^[^\'"@]+@(([\w-]\.?)+)$')

# regex for quick fullname check. No quotes or newlines allowed.
FULLNAME_REGEX= re.compile('[\'"\n]')

class InvalidEmail(Exception):
	def __init__(self, email):
		Exception.__init__(self, "Invalid email: %s" % email)

class InvalidFullname(Exception):
	def __init__(self, fullname):
		Exception.__init__(self,
				"Invalid characters found in full name: %s" % fullname)

def validate_email(email):
	if not EMAIL_REGEX.match(email):
		return False
	return True

def validate_fullname(fullname):
	if FULLNAME_REGEX.search(fullname):
		return False
	return True
