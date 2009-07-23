import sqlite3
from bootstrap import settings

db = sqlite3.connect(settings.sqlite_path)


def setup():
	"""Creates all necessary tables"""

	db.cursor().executescript("""
		CREATE TABLE users
		(
			id       integer primary key autoincrement,
			name     text not null unique, 
			password text not null,
			email    text,
			fullname text,
			is_admin bool default 0
		);

		CREATE TABLE groups
		(
			id   integer primary key autoincrement,
			name text not null unique
		);

		CREATE TABLE group_members
		(
			groupid integer references groups(id),
			userid  integer references user(id)
		);

		CREATE TABLE options
		(
			key   text primary key not null unique,
			value text not null unique
		);
	""")

# sqlite3 specific variables / functions

SQLIntegrityError = sqlite3.IntegrityError

def default_execute(cursor, query, args=(), commit=True):
	cursor.execute(query, args)
	if commit:
		db.commit()

def debug_execute(cursor, query, args=(), commit=True):
	dbg_sql = query.replace("?", '"%s"')
	print "DBG:", dbg_sql % args
	default_execute(cursor, query, args, commit=commit)

execute = default_execute
if hasattr(settings, "db_debug") and settings.db_debug:
	execute = debug_execute
