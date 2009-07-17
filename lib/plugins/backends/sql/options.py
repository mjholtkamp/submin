from __init__ import db, execute


def setup():
	"""Creates table and other setup"""
	c = db.cursor()
	execute(c, """
		CREATE TABLE options
		(
			key   text primary key not null unique,
			value text not null unique
		)
	""")

def row_dict(cursor, row):
	# description returns a tuple; the first entry is the name of the field
	# zip makes (field_name, field_value) tuples, which can be converted into
	# a dictionary
	return dict(zip([x[0] for x in cursor.description], row))

def value(self, key):
	execute(db.cursor(), "SELECT value FROM options WHERE key=?", (key,))
	row = cur.fetchone()
	if not row:
		return None

	return row[0]

def set_value(self, key, value):
	# sqlite specific INSERT OR REPLACE
	execute(db.cursor(), \
		"INSERT OR REPLACE INTO options (key, value) VALUES (?, ?)", \
		(key, value))

	backend.set_value(key, value)

def options(self):
	cur = db.cursor()
	execute(cur, "SELECT key, value FROM options)")
	row = cur.fetchall()
	if not row:
		return None

	return row_dict(cur, row)
