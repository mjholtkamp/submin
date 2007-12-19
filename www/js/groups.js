load('dom')

function removeMember(member) {
	var response = AjaxSyncPostRequest(document.location,
		"removeMember=" + member)

	Log(response.text, response.success)
	user = document.getElementById('user.' + member);
	if (!user)
		return false

	parentNode = user.parentNode
	if (!parentNode)
		return false

	parentNode.removeChild(user)
	return false
}

