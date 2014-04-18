"""Contains the scripts to create and update the database schema.

The list sql_scripts is listed in reverse order, so latest additions to the
schema are first in the list. The first entry in this list is always the
current schema version.
"""
sql_scripts = [
	(10, """-- first fix the unique contraint on permissions
		DROP TABLE IF EXISTS permissions_tmp;

		CREATE TABLE permissions_tmp (
			repository     text,
			repositorytype text,
			path           text not null,
			subjecttype    text not null,   -- user, group or all
			subjectid      integer,         -- only null if subjecttype is all
			type           text default '', -- '', 'r' or 'rw'
			UNIQUE(repository, repositorytype, path, subjecttype, subjectid)
		);

		INSERT INTO permissions_tmp (repository, repositorytype, path, subjecttype, subjectid, type)
			SELECT repository, repositorytype, path, subjecttype, subjectid, type FROM permissions;

		ALTER TABLE permissions RENAME TO permissions_old;
		ALTER TABLE permissions_tmp RENAME TO permissions;
		DROP TABLE permissions_old;

		-- now that the contraint is fixed, get rid of .git extensions
		UPDATE permissions
		SET repository = substr(repository, 1, length(repository) - 4)
		WHERE repositorytype = 'git' AND repository LIKE '%.git';

		-- do notifications as well
		UPDATE notifications
		SET repository = substr(repository, 1, length(repository) - 4)
		WHERE repositorytype = 'git' AND repository LIKE '%.git';
	"""),
	(9, """CREATE TABLE hook_jobs (
			jobid            integer primary key autoincrement,
			repository       text not null,
			repositorytype   text not null,
			hooktype         text not null,
			content          text not null
	);
	"""),
	(8, """DROP TABLE IF EXISTS notifications_tmp;
		CREATE TABLE notifications_tmp
		(
			userid       integer references users(id),
			repository   text,
			repositorytype text,
			PRIMARY KEY(userid, repository, repositorytype)
		);
		INSERT INTO notifications_tmp (userid, repository, repositorytype)
			SELECT userid, repository, CASE WHEN repository LIKE '%.git' THEN 'git' ELSE 'svn' END as repositorytype FROM notifications WHERE enabled=1;
		ALTER TABLE notifications RENAME TO notifications_old;
		ALTER TABLE notifications_tmp RENAME TO notifications;
		DROP TABLE notifications_old;
	"""),
	(7, """CREATE TABLE sessions
	(
		key   text not null primary key not null unique,
		value text not null -- pickled dictionary
	);
	"""),
	(6, """UPDATE options SET key='git_ssh_host_internal'
		          WHERE key='git_ssh_host';"""),
	(5, """UPDATE options SET key='git_ssh_port' WHERE key='ssh_port';
		   UPDATE options SET key='git_ssh_host' WHERE key='ssh_host';"""),
	(4, """CREATE TABLE password_reset (
			userid  integer not null references user(id) primary key, -- valid for this user
			expires integer not null, -- this entry expires at Unix Time
			key     text not null -- random secret 
		);"""),
	(3, """INSERT OR IGNORE INTO options VALUES ('git_dir', 'git');"""),
	(2, """CREATE TABLE ssh_keys
		(
			id      integer primary key autoincrement,
			userid  integer not null references user(id),
			title   text,
			ssh_key text not null
		);"""),
	(1, """CREATE TABLE users
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
			value text not null
		);

		CREATE TABLE notifications
		(
			userid       integer references users(id),
			repository   text,
			allowed      bool default 0,
			enabled      bool default 0,
			PRIMARY KEY(userid, repository)
		);

		CREATE TABLE permissions
		(
			repository     text,
			repositorytype text,
			path           text not null,
			subjecttype    text not null,   -- user, group or all
			subjectid      integer,         -- only null if subjecttype is all
			type           text default '', -- '', 'r' or 'rw'
			UNIQUE(repository, path, subjecttype, subjectid)
		);

		CREATE TABLE managers
		(
			id          integer primary key autoincrement,
			managertype text not null, -- user or group
			managerid   integer,
			objecttype  text not null, -- group or repository
			objectid    integer, -- groupid if objecttype is group
			objectname  text -- name of repository if objecttype is repository
		);""")
]
