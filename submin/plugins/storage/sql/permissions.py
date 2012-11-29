import submin.plugins.storage.sql.common as storage

def list_paths(repository, repostype):
	cur = storage.db.cursor()
	storage.execute(cur, """SELECT path FROM permissions WHERE repository = ?
		AND repositorytype = ? GROUP BY path""", (repository, repostype))
	rows = cur.fetchall()
	if not rows:
		return []

	return [x[0] for x in rows]

def list_permissions_by_user(username):
	cur = storage.db.cursor()
	userid = _subject_to_id(username, 'user')
	storage.execute(cur, """SELECT p.repository, p.repositorytype, p.path, p.type  FROM permissions AS p
		LEFT JOIN group_members AS gm ON p.subjectid=gm.groupid
		WHERE (subjecttype = 'group' AND gm.userid = ?) OR
			(subjecttype = 'user' and p.subjectid = ?)""", (userid, userid))

	rows = cur.fetchall()
	if not rows:
		return

	for row in rows:
		yield {
			'repository': row[0],
			'vcs': row[1],
			'path': row[2],
			'permission': row[3]
		}

def list_permissions(repos, repostype, path):
	cur = storage.db.cursor()

	queries = [
		"""SELECT users.name, subjecttype, type FROM permissions
			LEFT JOIN users ON permissions.subjectid = users.id
			WHERE repository = ? AND repositorytype = ?
				AND path = ? AND subjecttype = 'user'""",
		"""SELECT groups.name, subjecttype, type FROM permissions
			LEFT JOIN groups ON permissions.subjectid = groups.id
			WHERE repository = ? AND repositorytype = ?
				AND path = ? AND subjecttype = 'group'""",
		"""SELECT '*', subjecttype, type FROM permissions
			WHERE repository = ? AND repositorytype = ?
				AND path = ? AND subjecttype = 'all'"""
		]

	rows = []
	for query in queries:
		storage.execute(cur, query, (repos, repostype, path))

		current_rows = cur.fetchall()
		if current_rows:
			rows.extend(current_rows)

	if not rows:
		return []

	return [{'name': row[0], 'type': row[1], 'permission': row[2]} for row in rows]

def _subject_to_id(subject, subjecttype):
	cur = storage.db.cursor()
	tables = {'user': 'users', 'group': 'groups', 'all': None}
	table = tables[subjecttype]

	if table != None:
		storage.execute(cur, "SELECT id FROM %s WHERE name = ?" % table,
			(subject,))
		row = cur.fetchone()
		if not row:
			raise Exception("Unknown %s: %s" % (subjecttype, subject))

		subjectid = row[0]
	else:
		subjectid = None

	return subjectid

def add_permission(repos, repostype, path, subject, subjecttype, perm):
	cur = storage.db.cursor()
	subjectid = _subject_to_id(subject, subjecttype)

	storage.execute(cur, """INSERT INTO permissions
		(repository, repositorytype, path, subjectid, subjecttype, type)
		VALUES (?, ?, ?, ?, ?, ?)""",
		(repos, repostype, path, subjectid, subjecttype, perm))

def change_permission(repos, repostype, path, subject, subjecttype, perm):
	cur = storage.db.cursor()
	subjectid = _subject_to_id(subject, subjecttype)

	# testing for 'X = NULL' fails, should use 'X IS NULL'
	# but if we use ? for that case, we get the following error:
	#   OperationalError: near "?": syntax error
	# so instead we use this horrid construction
	test = "subjectid = ?"
	variables = (perm, repos, repostype, path, subjectid, subjecttype)
	if not subjectid:
		test = "subjectid IS NULL"
		variables = (perm, repos, repostype, path, subjecttype)

	storage.execute(cur, """UPDATE permissions
		SET type = ?
		WHERE repository = ? AND repositorytype = ? AND path = ? AND %s
		AND subjecttype = ?""" % test,
		variables)

def remove_permission(repos, repostype, path, subject, subjecttype):
	cur = storage.db.cursor()
	subjectid = _subject_to_id(subject, subjecttype)

	# testing for 'X = NULL' fails, should use 'X IS NULL'
	# but if we use ? for that case, we get the following error:
	#   OperationalError: near "?": syntax error
	# so instead we use this horrid construction
	test = "subjectid = ?"
	variables = (repos, repostype, path, subjectid, subjecttype)
	if not subjectid:
		test = "subjectid IS NULL"
		variables = (repos, repostype, path, subjecttype)

	storage.execute(cur, """DELETE FROM permissions WHERE repository = ?
		AND repositorytype = ? AND path = ?
		AND %s AND subjecttype = ?""" % test, variables)
