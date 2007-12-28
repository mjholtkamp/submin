
var sidebar_old_load = window.onload;
window.onload = function() {
	if (sidebar_old_load) sidebar_old_load()
	var users = document.getElementById('users')
	var groups = document.getElementById('groups')
	var deleters = users.getElementsByTagName('span')

	for (var idx = 0; idx < deleters.length; ++idx) {
		var deleter = deleters[idx]
		deleter.onclick = deleteObject
	}

	deleters = groups.getElementsByTagName('span')

	for (var idx = 0; idx < deleters.length; ++idx) {
		var deleter = deleters[idx]
		deleter.onclick = deleteObject
	}
}

function deleteObject()
{
	var div = this.parentNode.parentNode
	var type = ''
	switch (div.id) {
		case 'users':
		case 'groups':
			type = div.id
			break
		default:
			return
			break
	}
	var name = this.parentNode.firstChild.firstChild.nodeValue;
	var url = media_url + '/' + type + '/delete/' + name
	var response = AjaxSyncPostRequest(url, "")
	Log(response.text, response.success)
	if (response.success) {
		this.parentNode.parentNode.removeChild(this.parentNode)
	}
}
