load('dom')

function removeMember(member) {
	var response = AjaxSyncPostRequest(document.location,
		"removeMember=" + member)

	Log(response.text, response.success)
	return false
}

