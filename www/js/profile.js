load('dom')

function sendEmail() {
	var response = AjaxGetRequest("/ajax/profile/?" + "email=" + $('email').value)
	//$('response').innerHTML = response
}
