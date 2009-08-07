from __init__ import mock_groups

ids = 0

def clear_groups():
	mock_groups.clear()

class GroupExistsError(Exception):
	pass

def list():
	"""Generator for sorted list of groups"""
	return mock_groups.values()

def add(groupname):
	ids += 1
	mock_groups[groupname] = {'id': ids, 'name': groupname, 'members': []}

def group_data(groupname):
	return mock_group[groupname]

def remove_permissions_repository(groupid):
	pass

def remove_permissions_submin(groupid):
	pass

def remove_members_from_group(groupid):
	pass

def get_group_by_id(groupid):
	for key, value in mock_groups:
		if value["id"] == groupid:
			return value

def remove(groupid):
	group = get_group_by_id(groupid)
	del mock_groups[group["name"]]

def members(groupid):
	return get_group_by_id(groupid)['members']

def add_member(groupid, userid):
	get_group_by_id(groupid)['members'].append(userid)

def remove_member(groupid, userid):
	members = get_group_by_id(groupid)['members']
	for i in range(len(members)):
		if members[i] == userid:
			del members[i]
			break
