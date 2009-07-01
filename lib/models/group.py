from models import getBackend
backend = getBackend("group")

class UnknownGroupError(Exception):
	pass

class Group(object):
	@staticmethod
	def list():
		return [Group(raw_data=group) for group in backend.groups()]

	@staticmethod
	def add(name):
		"""Add a new, empty group"""
		backend.add(name)

	def __init__(self, groupname=None, raw_data=None):
		"""Constructor, either takes a groupname or raw data

		If groupname is provided, the backend is used to get the required data.
		If raw_data is provided, the backend is not used.
		"""
		db_group = raw_data

		if not raw_data:
			db_group = backend.get_data(groupname)
			if not db_group:
				raise UnknownGroupError(groupname)

		self._id   = db_group['id']
		self._name = db_group['name']

	def __str__(self):
		return self.name

	def members(self):
		return backend.members(self._id)

	def add_member(self, user):
		backend.add_member(self._id, user.id)

	# Properties
	def _getId(self):
		return self._id

	def _getName(self):
		return self._name

	id   = property(_getId)   # id is read-only
	name = property(_getName) # name is read-only
