load('dom')

function sendEmail() {
	var response = AjaxGetRequest(document.location + "?ajax&" + "email=" + $('email').value)
	Log(response.responseText, response.status != 200)
}

function sendPassword() {
	var response = AjaxGetRequest(document.location + "?ajax&" + "password=" + $('password').value)
	Log(response.responseText, response.status != 200)
}
