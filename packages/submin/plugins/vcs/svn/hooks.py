from export import export_authz, export_notifications

hooks = {
	'user-create': [export_authz],
	'user-delete': [export_authz, export_notifications],
	'user-update': [export_authz, export_notifications],
	'group-add-member': [export_authz, export_notifications],
	'group-delete-member': [export_authz, export_notifications],
	'group-delete': [export_authz, export_notifications],
	'repository-delete': [export_authz, export_notifications],
	'permission-update': [export_authz, export_notifications]
}