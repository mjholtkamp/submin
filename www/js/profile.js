load('dom')

function sendEmail() {
	var response = AjaxGetRequest("/ajax/profile/?" + "email=" + $('email').value)
	Log(response)
}

function sendPassword() {
	var response = AjaxGetRequest("/ajax/profile/?" + "password=" + $('password').value)
	Log(response)
}
