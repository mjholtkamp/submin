import sqlite3
from models.exceptions import BackendAlreadySetup

db = None
backend_debug = False

def close():
	if db:
		db.close()

def open(settings):
	global db, backend_debug
	db = sqlite3.connect(settings.sqlite_path)
	backend_debug = hasattr(settings, "db_debug") and settings.db_debug

def setup():
	"""Creates all necessary tables"""

	try:
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
			groupid integer not null references groups(id),
			userid  integer not null references user(id),
			PRIMARY KEY(groupid, userid)
		);

		CREATE TABLE options
		(
			key   text primary key not null unique,
			value text not null unique
		);

		CREATE TABLE notifications
		(
			userid       integer references users(id),
			repository   text,
			PRIMARY KEY(userid, repository)
		);

		CREATE TABLE permissions_repository
		(
			id           integer primary key autoincrement,
			repository   text,
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
			objectid    integer, -- groupid if objecttype is group
			objectname  text -- name of repository if objecttype is repository
		);
		""")
	except sqlite3.OperationalError, e:
		raise BackendAlreadySetup(str(e))

# sqlite3 specific variables / functions

SQLIntegrityError = sqlite3.IntegrityError

def default_execute(cursor, query, args=(), commit=True):
	try:
		cursor.execute(query, args)
	except:
		db.rollback()
		raise

	if commit:
		db.commit()

def debug_execute(cursor, query, args=(), commit=True):
	dbg_sql = query.replace("?", '"%s"')
	print "DBG:", dbg_sql % args
	default_execute(cursor, query, args, commit=commit)

execute = default_execute
if backend_debug:
	execute = debug_execute
