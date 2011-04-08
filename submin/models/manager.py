
class Manager(object):
	"""
	This abstract class represents something that can manage another object.

	Objects that can manage objects are:
	  * user -> group (add/remove members)
	  * group -> group (add/remove members) -- can a group manage itself? hmm
	  * user -> repository (set permissions, enable notifications)
	  * group -> repository (idem.)
	"""

	def canManage(self, other):
		"""Checks if this object is allowed to manage the 'other' object.
		This 'other' object can be a Group or Repository.
		"""

		_id = None
		_name = None
		if other._type == 'repository':
			_name = other.name
		else:
			_id = other._id

		perm = storage.get_permission(self._id, self._type, _id, _name, other._type)
		if perm:
			return True

		# maybe we doesn't have permission as user, but as a group?
		if self._type == 'user':
			for group_name in self.member_of():
				g = group.Group(group_name)
				perm = storage.get_permissions(group._id, group._type,
					_id, _name, other._type)
				if perm:
					return True

		return False
