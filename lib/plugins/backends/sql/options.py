from __init__ import db, execute

def value(key):
	cur = db.cursor()
	execute(cur, "SELECT value FROM options WHERE key=?", (key,))
	row = cur.fetchone()
	if not row:
		return None

	return row[0]

def set_value(key, value):
	# sqlite specific INSERT OR REPLACE
	execute(db.cursor(), \
		"INSERT OR REPLACE INTO options (key, value) VALUES (?, ?)", \
		(key, value))

def options():
	cur = db.cursor()
	execute(cur, "SELECT key, value FROM options")
	row = cur.fetchall()
	if not row:
		return None

	return row
