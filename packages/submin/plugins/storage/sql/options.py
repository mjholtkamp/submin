import submin.plugins.storage.sql.common as storage
from submin.models.exceptions import UnknownKeyError

def value(key):
	cur = storage.db.cursor()
	storage.execute(cur, "SELECT value FROM options WHERE key=?", (key,))
	row = cur.fetchone()
	if not row:
		raise UnknownKeyError

	return row[0]

def set_value(key, value):
	# sqlite specific INSERT OR REPLACE
	storage.execute(storage.db.cursor(), """INSERT OR REPLACE INTO options
		(key, value) VALUES (?, ?)""", (key, value))

def unset_value(key):
	storage.execute(storage.db.cursor(), """DELETE FROM options
		WHERE key=?""", (key, ))

def options():
	cur = storage.db.cursor()
	storage.execute(cur, "SELECT key, value FROM options")
	row = cur.fetchall()
	if not row:
		return []

	return row
