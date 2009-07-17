from __init__ import db, execute

def setup():
	"""Creates table and other setup"""
	c = db.cursor()
	execute(c, """
		CREATE TABLE groups
		(
			id   integer primary key autoincrement,
			name text not null unique
		)
	""")

	execute(c, """
		CREATE TABLE group_members
		(
			groupid integer references groups(id),
			userid  integer references user(id)
		)
	""")


def row_dict(cursor, row):
	# description returns a tuple; the first entry is the name of the field
	# zip makes (field_name, field_value) tuples, which can be converted into
	# a dictionary
	return dict(zip([x[0] for x in cursor.description], row))

all_fields = "id, name"

def list():
	"""Generator for sorted list of groups"""
	cur = db.cursor()
	execute(cur, """
		SELECT %s
		FROM groups
		ORDER BY name ASC
	""" % all_fields)
	for x in cur:
		yield row_dict(cur, x)

def add(groupname):
	execute(db.cursor(), "INSERT INTO groups (name) VALUES (?)", (groupname,))

def group_data(groupname):
	cur = db.cursor()
	execute(cur, """
		SELECT %s
		FROM groups
		WHERE name=?""" % all_fields, (groupname,))
	row = cur.fetchone()
	if not row:
		return None

	return row_dict(cur, row)

def remove(groupid):
	execute(db.cursor(), "DELETE FROM groups WHERE id=?", (groupid,))

def members(groupid):
	"""Returns a sorted list of usernames, which are members of the group with
	id <groupid>"""
	cur = db.cursor()
	execute(cur, """
		SELECT users.name
		FROM group_members
		LEFT JOIN users ON group_members.userid = users.id
		WHERE group_members.groupid = ?
		ORDER BY users.name ASC
	""", (groupid,))
	for x in cur:
		yield x[0]

def add_member(groupid, userid):
	execute(db.cursor(), """
		INSERT INTO group_members
			(groupid, userid)
		VALUES
			(?, ?)
		""", (groupid, userid))

def remove_member(groupid, userid):
	execute(db.cursor(), """
		DELETE FROM group_members
		WHERE groupid=? AND userid=?
		""", (groupid, userid))

