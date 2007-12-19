load('dom')

// Using window.onload because an onclick="..." handler doesn't give the
// handler a this-variable
var old_load = window.onload;
window.onload = function() {
	if (old_load) old_load();
	$('password_button').onclick = verifyPassword;
}

function sendEmail() {
	var response = AjaxSyncPostRequest(document.location,
		"email=" + $('email').value)

	Log(response.text, response.success)
}

// global variable to temporarily store the password to be verified
var enteredPassword;
function verifyPassword() {
	enteredPassword = $('password').value;
	if (!enteredPassword) {
		Log('Please enter a password before pressing "change"', false);
		return false;
	}

	// Some cleaning up.
	$('password').value = '';
	this.parentNode.firstChild.innerHTML = 'Verify';
	$('password').focus();
	// change te onclick handler
	this.onclick = checkPasswords;
	return false;
}

function checkPasswords() {
	// Again some cleaning up.
	this.parentNode.firstChild.innerHTML = 'Password';
	// Make sure the change-button isn't highlighted anymore
	this.blur();
	// change the onclick handler back to the verifyPassword function
	this.onclick = verifyPassword;

	// Do the check after cleaning up.
	if ($('password').value != enteredPassword) {
		Log('Verification of password failed', false);
		enteredPassword = '';
		$('password').value = '';
		return false;
	}

	enteredPassword = '';
	$('password').value = '';

	// Send the entered password to the server.
	sendPassword(enteredPassword);
	return false;
}

function sendPassword(password) {
	var response = AjaxSyncPostRequest(document.location,
		"password=" + password)

	Log(response.text, response.success)
}
