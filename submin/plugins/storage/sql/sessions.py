import submin.plugins.storage.sql.common as storage
from submin.models.exceptions import UnknownKeyError

def value(key):
	cur = storage.db.cursor()
	storage.execute(cur, "SELECT value FROM sessions WHERE key=?", (key,))
	row = cur.fetchone()
	if not row:
		raise UnknownKeyError(key)

	return row[0]

def set_value(key, value):
	# sqlite specific INSERT OR REPLACE
	storage.execute(storage.db.cursor(), """INSERT OR REPLACE INTO sessions
		(key, value) VALUES (?, ?)""", (key, value))


def unset_value(key):
	storage.execute(storage.db.cursor(), """DELETE FROM sessions
		WHERE key=?""", (key, ))
