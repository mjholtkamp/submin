load('dom')

var old_load = window.onload;
window.onload = function() {
	if (old_load) old_load();
	$('password_button').onclick = verifyPassword;
}

function sendEmail() {
	var response = AjaxSyncPostRequest(document.location,
		"ajax&" + "email=" + $('email').value)

	Log(response.responseText, response.status != 200)
}

var enteredPassword;

function verifyPassword() {
	enteredPassword = $('password').value;
	if (!enteredPassword) {
		Log('Please enter a password before pressing "change"', true);
		return false;
	}

	$('password').value = '';
	this.parentNode.firstChild.innerHTML = 'Verify';
	this.onclick = checkPasswords;
	$('password').focus();
	return false;
}

function checkPasswords() {
	if ($('password').value != enteredPassword) {
		Log('Verification of password failed', true);
		return false;
	}

	enteredPassword = '';
	$('password').value = '';
	this.parentNode.firstChild.innerHTML = 'Password';
	this.onclick = verifyPassword;
	this.blur();
	sendPassword(enteredPassword);
	return false;
}

function sendPassword(password) {
	var response = AjaxSyncPostRequest(document.location,
		"ajax&" + "password=" + password)

	if (!response.responseText) {
		responseText = 'Server did report an error, but response text was empty'
	} else {
		responseText = response.responseText
	}
	Log(responseText, response.status != 200)
}
