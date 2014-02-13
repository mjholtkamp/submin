from submin.auth.export import export_htpasswd
hooks = {
	'user-update': [export_htpasswd],
	'user-delete': [export_htpasswd],
	'user-create': [export_htpasswd]
}
