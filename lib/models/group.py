from models import getBackend
backend = getBackend("group")

class UnknownGroupError(Exception):
	pass

class Group(object):
	@staticmethod
	def list():
		return [Group(raw_data=group) for group in backend.list()]

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
			db_group = backend.group_data(groupname)
			if not db_group:
				raise UnknownGroupError(groupname)

		self._id   = db_group['id']
		self._name = db_group['name']

	def __str__(self):
		return self.name

	def remove(self):
		backend.remove(self._id)

	def members(self):
		return backend.members(self._id)

	def add_member(self, user):
		backend.add_member(self._id, user.id)

	def remove_member(self, user):
		backend.remove_member(self._id, user.id)

	# Properties
	def _getId(self):
		return self._id

	def _getName(self):
		return self._name

	id   = property(_getId)   # id is read-only
	name = property(_getName) # name is read-only

__doc__ = """
Backend contract
================

Username is unique and primary key.

* list()
	Returns a sorted list of groups, sorted by groupname

* add(groupname)
	Adds a new group, raises `GroupExistsError` if there already is a group
	with this groupname

* group_data(groupname)
	Returns a dictionary with all required group data.
	Returns `None` if no group with this username exists.
	Fields which need to be implemented (with properties?): name
	
* remove(groupid)
	Removes group with id *groupid*.

* setup()
	Creates the sql-table or performs other setup

* members(groupid)
	Returns a sorted list of members, sorted by username, for group with id
	*groupid*

* add_member(groupid, userid)
	Adds the user with id *userid* to the group with id *groupid*

* remove_member(groupid, userid)
	Removes the user with id *userid* from the group with id *groupid*
"""
