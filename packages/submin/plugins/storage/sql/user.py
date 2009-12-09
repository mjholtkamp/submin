import submin.plugins.storage.sql.common as storage
from submin.models.exceptions import UserExistsError, NoMD5PasswordError
from submin.auth import md5crypt

def row_dict(cursor, row):
	# description returns a tuple; the first entry is the name of the field
	# zip makes (field_name, field_value) tuples, which can be converted into
	# a dictionary
	return dict(zip([x[0] for x in cursor.description], row))

all_fields = "id, name, email, fullname, is_admin"

def list():
	"""Generator for sorted list of users"""
	cur = storage.db.cursor()
	storage.execute(cur, """
		SELECT %s
		FROM users
		ORDER BY name ASC
	""" % all_fields)
	for x in cur:
		yield row_dict(cur, x)

def _pw_hash(password, salt=None, magic='apr1'):
	if salt is None:
		salt = md5crypt.makesalt()
	newhash = md5crypt.md5crypt(password, salt, '$' + magic + '$')
	return newhash

def add(username, password):
	if password:
		password = _pw_hash(password)
	else:
		password = ""

	cur = storage.db.cursor()
	try:
		storage.execute(cur, "INSERT INTO users (name, password) VALUES (?, ?)",
				(username, password))
	except storage.SQLIntegrityError, e:
		raise UserExistsError("User `%s' already exists" % username)

def check_password(userid, password):
	cur = storage.db.cursor()
	storage.execute(cur, "SELECT password FROM users WHERE id=?", (userid,))
	row = cur.fetchone()
	vals = row[0][1:].split('$')
	if not len(vals) == 3:
		raise NoMD5PasswordError
	magic, salt, encrypted = vals
	return _pw_hash(password, salt, magic) == row[0]

def set_password(userid, password):
	password = _pw_hash(password)
	set_md5_password(userid, password)

def set_md5_password(userid, password):
	storage.execute(storage.db.cursor(), """UPDATE users
		SET password=? WHERE id=?""", (password, userid))

# Remove functions, removes users from various tables
def remove_from_groups(userid):
	storage.execute(storage.db.cursor(), """DELETE FROM group_members
		WHERE userid=?""", (userid,))

def remove_permissions_repository(userid):
	storage.execute(storage.db.cursor(), """DELETE FROM permissions
		WHERE subjecttype="user" AND subjectid=?""", (userid,))

def remove_permissions_submin(userid):
	storage.execute(storage.db.cursor(), """DELETE FROM managers
		WHERE managertype="user" AND managerid=?""", (userid,))

def remove_notifications(userid):
	storage.execute(storage.db.cursor(), """DELETE FROM notifications
		WHERE userid=?""", (userid,))

def remove(userid):
	storage.execute(storage.db.cursor(), """DELETE FROM users
		WHERE id=?""", (userid,))

def notification(userid, repository):
	cur = storage.db.cursor()
	storage.execute(cur, """
		SELECT allowed, enabled
		FROM notifications
		WHERE userid=? AND repository=?""", (userid, repository))
	row = cur.fetchone()
	if not row:
		return None

	return row_dict(cur, row)

def set_notification(userid, repository, allowed, enabled):
	try:
		storage.execute(storage.db.cursor(), """INSERT INTO notifications
		(userid, repository, allowed, enabled) VALUES (?, ?, ?, ?)""", 
			(userid, repository, allowed, enabled))
	except storage.SQLIntegrityError:
		# already exists?
		storage.execute(storage.db.cursor(), """UPDATE notifications
		SET allowed = ?, enabled = ? WHERE userid = ? AND repository = ? """,
		 (allowed, enabled, userid, repository))

def user_data(username):
	cur = storage.db.cursor()
	storage.execute(cur, """
		SELECT %s
		FROM users
		WHERE name=?""" % all_fields, (username,))
	row = cur.fetchone()
	if not row:
		return None

	return row_dict(cur, row)

def field_setter(field):
	def set_field(userid, value):
		cur = storage.db.cursor()
		sql = "UPDATE users SET %s=? WHERE id=?" % field
		storage.execute(cur, sql, (value, userid))
	return set_field

def field_setter_bool(field):
	def set_field_bool(userid, value):
		if value == True or value == 'true' or value == '1':
			value = 1
		else:
			value = 0

		cur = storage.db.cursor()
		sql = "UPDATE users SET %s=? WHERE id=?" % field
		storage.execute(cur, sql, (value, userid))
	return set_field_bool

set_name     = field_setter("name")
set_email    = field_setter("email")
set_fullname = field_setter("fullname")
set_is_admin = field_setter_bool("is_admin")


member_query = """
		SELECT groups.name FROM group_members
		LEFT JOIN groups ON group_members.groupid %s groups.id
		WHERE group_members.userid = ?
		ORDER BY groups.name ASC
"""

def member_of(userid):
	"""Returns list of groups a user is a member of"""
	cur = storage.db.cursor()
	storage.execute(cur, member_query % "=", (userid,))

	return [row[0] for row in cur]

def nonmember_of(userid):
	"""Returns list of groups a user is not a member of"""
	cur = storage.db.cursor()
	storage.execute(cur, member_query % "!=", (userid,))

	return [row[0] for row in cur]
