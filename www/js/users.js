load('dom')

function sendEmail() {
	var response = AjaxGetRequest(document.location + "?ajax&" + "email=" + $('email').value)
	Log(response.responseText, response.status != 200)
}

function sendPassword() {
	var response = AjaxGetRequest(document.location + "?ajax&" + "password=" + $('password').value)
	if (!response.responseText) {
		responseText = 'Server did report an error, but response text was empty'
	} else {
		responseText = response.responseText
	}
	Log(responseText, response.status != 200)
}
