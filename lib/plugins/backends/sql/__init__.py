import sqlite3

backend_debug = False
db = object()

def teardown():
	db.close()

def init(settings):
	global db, backend_debug
	db = sqlite3.connect(settings.sqlite_path)
	backend_debug = hasattr(settings, "db_debug") and settings.db_debug

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

		CREATE TABLE repositories
		(
			id   integer primary key autoincrement,
			name text not null
		);

		CREATE TABLE notifications
		(
			id           integer primary key autoincrement,
			userid       integer references users(id),
			repositoryid integer references repositories(id),
			allowed      bool default 0,
			enabled      bool default 0
		);

		CREATE TABLE permissions_repository
		(
			id           integer primary key autoincrement,
			repositoryid integer references repositories(id),
			path         text not null,
			subjecttype  text not null, -- user, group or all
			subjectid    integer,       -- only null if subjecttype is all
			type         text           -- '', 'r' or 'rw'
		);

		CREATE TABLE permissions_submin
		(
			id          integer primary key autoincrement,
			subjecttype text not null, -- user or group
			subjectid   integer,
			objecttype  text not null, -- group or repository
			objectid    integer
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
if backend_debug:
	execute = debug_execute
