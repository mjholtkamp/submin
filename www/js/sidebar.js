
var sidebar_old_load = window.onload;
window.onload = function() {
	if (sidebar_old_load) sidebar_old_load()
	var users = document.getElementById('users')
	var deleters = users.getElementsByTagName('span')

	for (var idx = 0; idx < deleters.length; ++idx) {
		var deleter = deleters[idx]
		deleter.onclick = deleteUser
	}
}

function deleteUser()
{
	var user = this.parentNode.firstChild.firstChild.nodeValue;
	var url = media_url + '/users/delete/' + user
	var response = AjaxSyncPostRequest(url, "")
	Log(response.text, response.success)
	if (response.success) {
		this.parentNode.parentNode.removeChild(this.parentNode)
	}
}
