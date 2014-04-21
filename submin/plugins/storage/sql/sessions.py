import submin.plugins.storage.sql.common as storage
from submin.models.exceptions import UnknownKeyError

def get(key):
	cur = storage.db.cursor()
	storage.execute(cur, "SELECT value, expires FROM sessions WHERE key=?", (key,))
	row = cur.fetchone()
	if not row:
		raise UnknownKeyError(key)

	return (row[0], row[1])

def set(key, value, expires):
	# sqlite specific INSERT OR REPLACE
	storage.execute(storage.db.cursor(), """INSERT OR REPLACE INTO sessions
		(key, value, expires) VALUES (?, ?, ?)""", (key, value, expires))

def unset(key):
	storage.execute(storage.db.cursor(), """DELETE FROM sessions
		WHERE key=?""", (key, ))
