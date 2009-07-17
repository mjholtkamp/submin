import sqlite3
from bootstrap import settings

db = sqlite3.connect(settings.sqlite_path)

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
