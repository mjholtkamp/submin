import sqlite3
import plugins.backends.sql.common as backend
from models.exceptions import GroupExistsError, MemberExistsError

def row_dict(cursor, row):
	# description returns a tuple; the first entry is the name of the field
	# zip makes (field_name, field_value) tuples, which can be converted into
	# a dictionary
	return dict(zip([x[0] for x in cursor.description], row))

all_fields = "id, name"

def list():
	"""Generator for sorted list of groups"""
	cur = backend.db.cursor()
	backend.execute(cur, """
		SELECT %s
		FROM groups
		ORDER BY name ASC
	""" % all_fields)
	for x in cur:
		yield row_dict(cur, x)

def add(groupname):
	try:
		backend.execute(backend.db.cursor(), \
			"INSERT INTO groups (name) VALUES (?)", (groupname,))
	except backend.SQLIntegrityError, e:
		raise GroupExistsError("Group `%s' already exists" % groupname)

def group_data(groupname):
	cur = backend.db.cursor()
	backend.execute(cur, """
		SELECT %s
		FROM groups
		WHERE name=?""" % all_fields, (groupname,))
	row = cur.fetchone()
	if not row:
		return None

	return row_dict(cur, row)

def remove_permissions(groupid):
	backend.execute(backend.db.cursor(), """DELETE FROM permissions
		WHERE subjecttype="group" AND subjectid=?""", (groupid,))

def remove_managers(groupid):
	backend.execute(backend.db.cursor(), """DELETE FROM managers
		WHERE managertype="group" AND managerid=?""", (groupid,))

def remove_members_from_group(groupid):
	backend.execute(backend.db.cursor(), """DELETE FROM group_members
		WHERE groupid=?""", (groupid,))

def remove(groupid):
	backend.execute(backend.db.cursor(), """DELETE FROM groups
		WHERE id=?""", (groupid,))

def members(groupid):
	"""Returns a sorted list of usernames, which are members of the group with
	id <groupid>"""
	cur = backend.db.cursor()
	backend.execute(cur, """
		SELECT users.name
		FROM group_members
		LEFT JOIN users ON group_members.userid = users.id
		WHERE group_members.groupid = ?
		ORDER BY users.name ASC
	""", (groupid,))
	for x in cur:
		yield x[0]

def add_member(groupid, userid):
	try:
		backend.execute(backend.db.cursor(), """
			INSERT INTO group_members
				(groupid, userid)
			VALUES
				(?, ?)
			""", (groupid, userid))
	except sqlite3.IntegrityError:
		raise MemberExistsError

def remove_member(groupid, userid):
	backend.execute(backend.db.cursor(), """
		DELETE FROM group_members
		WHERE groupid=? AND userid=?
		""", (groupid, userid))

