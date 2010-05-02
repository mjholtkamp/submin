import sqlite3
from submin.models.exceptions import StorageAlreadySetup
from submin.plugins.storage.sql import schema

db = None
storage_debug = False
schema_version = schema.sql_scripts[0][0]

class FutureDatabaseException(Exception):
	def __init__(self):
		Exception.__init__(self, "Database is newer than code, please upgrade the code. Aborting to prevent data loss")

def close():
	if db:
		db.close()

def open(settings):
	global db, storage_debug
	db = sqlite3.connect(settings.sqlite_path)
	storage_debug = hasattr(settings, "db_debug") and settings.db_debug

def live_database_version():
	"""Returns the version of the database which is currently in production"""

	cursor = db.cursor()
	try:
		cursor.execute(
			"SELECT value from options where key=?", ("database_version",))
		row = cursor.fetchone()
		return int(row[0])
	except sqlite3.OperationalError, e:
		return 0

def database_isuptodate():
	data_version = live_database_version()
	if data_version > schema_version:
		raise FutureDatabaseException()
	return schema_version == data_version

def database_backup(settings):
	from shutil import copyfile
	from time import strftime
	backupname = settings.sqlite_path + "-" + strftime("%Y%m%d%H%M%S")
	copyfile(settings.sqlite_path, backupname)

def database_evolve(verbose=False):
	"""Upgrades the database to the latest version."""
	live_version = live_database_version()
	start = live_version
	end = schema_version
	if (start > end):
		raise FutureDatabaseException()

	cursor = db.cursor()
	for version, script in list(reversed(schema.sql_scripts))[start:end]:
		if verbose:
			print "Evolving database from version", (version - 1), "to", version
		try:
			cursor.executescript(script)
		except Exception, e:
			print "Error while evolving database to version", version
			print "Now rolling back to", start
			db.rollback()
			raise
	if start > 0:
		cursor.execute(
				"UPDATE options SET value=? WHERE key='database_version'",
				(schema_version,))
	else:
		cursor.execute(
			"INSERT INTO options (key, value) VALUES ('database_version', ?)",
			(schema_version,))
	db.commit()
	if verbose:
		print "Database is now at version", schema_version

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
if storage_debug:
	execute = debug_execute
