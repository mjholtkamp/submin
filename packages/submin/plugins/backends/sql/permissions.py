import submin.plugins.backends.sql.common as backend

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

def _subject_to_id(subject, subjecttype):
	cur = backend.db.cursor()
	tables = {'user': 'users', 'group': 'groups', 'all': None}
	table = tables[subjecttype]

	if table != None:
		backend.execute(cur, "SELECT id FROM %s WHERE name = ?" % table,
			(subject,))
		row = cur.fetchone()
		if not row:
			raise Exception("Unknown %s: %s" % (subjecttype, subject))

		subjectid = row[0]
	else:
		subjectid = None

	return subjectid

def add_permission(repos, path, subject, subjecttype, perm):
	cur = backend.db.cursor()
	subjectid = _subject_to_id(subject, subjecttype)

	backend.execute(cur, """INSERT INTO permissions
		(repository, path, subjectid, subjecttype, type)
		VALUES (?, ?, ?, ?, ?)""",
		(repos, path, subjectid, subjecttype, perm))

def change_permission(repos, path, subject, subjecttype, perm):
	cur = backend.db.cursor()
	subjectid = _subject_to_id(subject, subjecttype)

	# testing for 'X = NULL' fails, should use 'X IS NULL'
	# but if we use ? for that case, we get the following error:
	#   OperationalError: near "?": syntax error
	# so instead we use this horrid construction
	test = "subjectid = ?"
	variables = (perm, repos, path, subjectid, subjecttype)
	if not subjectid:
		test = "subjectid IS NULL"
		variables = (perm, repos, path, subjecttype)

	backend.execute(cur, """UPDATE permissions
		SET type = ?
		WHERE repository = ? AND path = ? AND %s
		AND subjecttype = ?""" % test,
		variables)

def remove_permission(repos, path, subject, subjecttype):
	cur = backend.db.cursor()
	subjectid = _subject_to_id(subject, subjecttype)

	# testing for 'X = NULL' fails, should use 'X IS NULL'
	# but if we use ? for that case, we get the following error:
	#   OperationalError: near "?": syntax error
	# so instead we use this horrid construction
	test = "subjectid = ?"
	variables = (repos, path, subjectid, subjecttype)
	if not subjectid:
		test = "subjectid IS NULL"
		variables = (repos, path, subjecttype)

	backend.execute(cur, """DELETE FROM permissions WHERE repository = ?
		AND path = ? AND %s AND subjecttype = ?""" % test, variables)
