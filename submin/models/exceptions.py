"""This module is a central place for exceptions so circular imports are not
needed"""

####### Options exceptions ###################################################

class UnknownKeyError(Exception):
	"""Used in Options whenever a value is requested of a key that does not exist"""
	pass

class MissingConfig(Exception):
	pass


####### Storage exceptions ###################################################

class StorageAlreadySetup(Exception):
	"""When a storage is already setup"""
	pass

class StorageError(Exception):
	"""Generic storage exception, probably settings are incorrect"""
	pass


####### User exceptions ######################################################

class UserExistsError(Exception):
	pass

class NoMD5PasswordError(Exception):
	def __init__(self):
		Exception.__init__(self, "Password is not encrypted with MD5")

class MD5NotSupportedError(Exception):
	pass

class UnknownUserError(Exception):
	pass

class UserPermissionError(Exception):
	"""User has no permission to make this change"""
	pass

####### Group exceptions #####################################################

class GroupExistsError(Exception):
	pass

class MemberExistsError(Exception):
	pass

class UnknownGroupError(Exception):
	pass


####### Email exceptions #####################################################

class SendEmailError(Exception):
	pass
	
####### VCS Exceptions #######################################################

class InvalidPermissionError(Exception):
	"""Permission is not valid for this vcs"""
	pass

