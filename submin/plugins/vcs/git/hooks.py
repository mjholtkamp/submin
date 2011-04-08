from submin.plugins.vcs.git.export import export_ssh_keys

hooks = {
	'user-update': [export_ssh_keys],
}
