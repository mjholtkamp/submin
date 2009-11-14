import submin.plugins.backends.sql.common as backend
from submin.models.exceptions import UnknownKeyError

def value(key):
	cur = backend.db.cursor()
	backend.execute(cur, "SELECT value FROM options WHERE key=?", (key,))
	row = cur.fetchone()
	if not row:
		raise UnknownKeyError

	return row[0]

def set_value(key, value):
	# sqlite specific INSERT OR REPLACE
	backend.execute(backend.db.cursor(), """INSERT OR REPLACE INTO options
		(key, value) VALUES (?, ?)""", (key, value))

def options():
	cur = backend.db.cursor()
	backend.execute(cur, "SELECT key, value FROM options")
	row = cur.fetchall()
	if not row:
		return []

	return row
