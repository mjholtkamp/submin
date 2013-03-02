from submin.plugins.vcs.git.export import export_ssh_keys, export_notifications

hooks = {
	'user-update': [export_ssh_keys, export_notifications],
	'user-delete': [export_notifications],
	'user-notifications-update': [export_notifications],
	'group-add-member': [export_notifications],
	'group-delete-member': [export_notifications],
	'group-delete': [export_notifications],
	'repository-delete': [export_notifications],
	'repository-notifications-update': [export_notifications],
	'permission-update': [export_notifications]
}
