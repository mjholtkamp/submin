import submin.plugins.storage.sql.common as storage

def jobs(repositorytype, repository, hooktype):
	cur = storage.db.cursor()
	storage.execute(cur, """SELECT jobid, content FROM hook_jobs
		WHERE repositorytype=? AND repository=? AND hooktype=?""",
		(repositorytype, repository, hooktype))
	row = cur.fetchall()
	if not row:
		return []

	return row

def queue(repositorytype, repository, hooktype, content):
	# sqlite specific INSERT OR REPLACE
	storage.execute(storage.db.cursor(), """INSERT INTO hook_jobs
		(repositorytype, repository, hooktype, content)
		VALUES (?, ?, ?, ?)""",
		(repositorytype, repository, hooktype, content))

def done(jobid):
	storage.execute(storage.db.cursor(), """DELETE FROM hook_jobs
		WHERE jobid=?""", (jobid, ))


