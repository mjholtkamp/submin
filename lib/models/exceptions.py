"""This module is a central place for exceptions so circular imports are not
needed"""

####### Options exceptions ###################################################

class UnknownKeyError(Exception):
	"""Used in Options whenever a value is requested of a key that does not exist"""
	pass


####### Backend exceptions ###################################################

class BackendAlreadySetup(Exception):
	"""When a backend is already setup"""
	pass

class BackendError(Exception):
	"""Generic backend exception, probably settings are incorrect"""
	pass


####### User exceptions ######################################################

class UserExistsError(Exception):
	pass

class NoMD5PasswordError(Exception):
	def __init__(self):
		Exception.__init__(self, "Password is not encrypted with MD5")

####### Group exceptions #####################################################

class GroupExistsError(Exception):
	pass

class MemberExistsError(Exception):
	pass

class UnknownGroupError(Exception):
	pass
