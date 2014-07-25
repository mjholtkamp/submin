import re

# regex for quick email check. No quotes allowed, be very allowing
# for domain-names and ip-addresses.
EMAIL_REGEX = re.compile('^[^\'"@]+@(([\w-]\.?)+)$')

# Usernames can not contain newlines or quotes (due to restrictions in authz)
USERNAME_REGEX = re.compile('[\n\'"]')

# regex for quick fullname check. No quotes or newlines allowed.
FULLNAME_REGEX = re.compile('[\'"\n]')

class ssh_key_type:
	OpenSSH, RFC4716, PKCS8, PEM = 0, 1, 2, 3

# list of tuples of types and their regexes
ssh_key_types_regexes = [
	(ssh_key_type.OpenSSH, re.compile('^ssh-\w{3} [^ ]+( .+)?$')),
	(ssh_key_type.RFC4716, re.compile('^---- BEGIN SSH2 PUBLIC KEY ----')),
	(ssh_key_type.PKCS8, re.compile('^-----BEGIN PUBLIC KEY-----')),
	(ssh_key_type.PEM, re.compile('^-----BEGIN RSA PUBLIC KEY-----')),
]

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

class InvalidSSHKey(Exception):
	def __init__(self, ssh_key):
		Exception.__init__(self,
				"No valid SSH Key provided: %s" % ssh_key)

def validate_email(email):
	return EMAIL_REGEX.match(email)

def validate_username(user):
	return not USERNAME_REGEX.search(user)

def validate_fullname(fullname):
	return not FULLNAME_REGEX.search(fullname)

def detect_ssh_key(ssh_key):
	for (keytype, regex) in ssh_key_types_regexes:
		if regex.search(ssh_key):
			return keytype

	raise InvalidSSHKey(ssh_key)
