import plugins.backends.sql.common as backend

def list_paths(repository):
	cur = backend.db.cursor()
	backend.execute(cur, """SELECT path FROM permissions WHERE repository = ?
		GROUP BY path""", (repository,))
	rows = cur.fetchall()
	if not rows:
		return []

	return [x[0] for x in rows]

def list_permissions(repos, path):
	cur = backend.db.cursor()
	
	queries = [
		"""SELECT users.name, subjecttype, type FROM permissions
			LEFT JOIN users ON permissions.subjectid = users.id
			WHERE repository = ? AND path = ? AND subjecttype = 'user'""",
		"""SELECT groups.name, subjecttype, type FROM permissions
			LEFT JOIN groups ON permissions.subjectid = groups.id
			WHERE repository = ? AND path = ? AND subjecttype = 'group'""",
		"""SELECT '*', subjecttype, type FROM permissions
			WHERE repository = ? AND path = ? AND subjecttype = 'all'"""
		]

	rows = []
	for query in queries:
		backend.execute(cur, query, (repos, path))

		current_rows = cur.fetchall()
		if current_rows:
			rows.extend(current_rows)

	if not rows:
		return {}

	return [{'name': row[0], 'type': row[1], 'permission': row[2]} for row in rows]

def set_permission(repos, path, subject, subjecttype, perm):
	pass

def remove_permission(repos, path, subject, subjecttype):
	pass
