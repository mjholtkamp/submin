"""Contains the scripts to create and update the database schema.

The list sql_scripts is listed in reverse order, so latest additions to the
schema are first in the list. The first entry in this list is always the
current schema version.
"""
sql_scripts = [
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
