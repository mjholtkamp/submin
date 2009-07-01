from __init__ import db, execute
from config.authz import md5crypt

def setup():
	"""Creates table and other setup"""
	execute(db.cursor(), """
		CREATE TABLE user
		(
			name     text not null unique primary key, 
			password text not null,
			email    text,
			fullname text,
			is_admin bool default 0
		)
	""")

def row_dict(cursor, row):
	# description returns a tuple; the first entry is the name of the field
	# zip makes (field_name, field_value) tuples, which can be converted into
	# a dictionary
	return dict(zip([x[0] for x in cursor.description], row))

def users():
	"""Generator for sorted list of users"""
	cur = db.cursor()
	execute(cur, """
		SELECT name, email, fullname, is_admin
		FROM user
		ORDER BY name ASC
	""")
	for x in cur:
		yield row_dict(cur, x)

def add(username, password):
	magic = 'apr1'
	salt = md5crypt.makesalt()
	newhash = md5crypt.md5crypt(password, salt, '$' + magic + '$')

	cur = db.cursor()
	execute(cur, "INSERT INTO user (name, password) VALUES (?, ?)",
			(username, password))

def remove(username):
	execute(db.cursor(), "DELETE FROM user WHERE name=?", (username,))

def get_data(username):
	cur = db.cursor()
	execute(cur, """
		SELECT name, email, fullname, is_admin
		FROM user
		WHERE name=?""", (username,))
	row = cur.fetchone()
	if not row:
		return None

	return row_dict(cur, row)

def field_setter(field):
	def set_field(username, value):
		cur = db.cursor()
		sql = "UPDATE user SET %s=? WHERE name=?" % field
		execute(cur, sql, (value, username))
	return set_field

set_email    = field_setter("email")
set_fullname = field_setter("fullname")
set_is_admin = field_setter("is_admin")
