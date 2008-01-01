load('dom')

// Using window.onload because an onclick="..." handler doesn't give the
// handler a this-variable
var old_load = window.onload;
window.onload = function() {
	if (old_load) old_load();
	$('password_button').onclick = verifyPassword;

	// Initialize the select-dropdown
	selectInit();
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

	$('password').value = '';

	// Send the entered password to the server.
	sendPassword(enteredPassword);
	enteredPassword = '';
	return false;
}

function sendPassword(password) {
	var response = AjaxSyncPostRequest(document.location,
		"password=" + password)

	Log(response.text, response.success)
}


/*
 * Adding users to groups and removing them from groups
 */
function addMemberToGroupAjax(group) {
	var response = AjaxSyncPostRequest(document.location,
			"addToGroup=" + group)
	Log(response.text, response.success)
	return response.success
}

function removeMemberFromGroupAjax(group) {
	var response = AjaxSyncPostRequest(document.location,
			"removeFromGroup=" + group)
	Log(response.text, response.success)
	return response.success
}

var selectli = null;
function remove() {
	var value = this.parentNode.firstChild.firstChild.nodeValue;

	if (value == "---")
		return false;

	// Do the serverside thing!
	var success = removeMemberFromGroupAjax(value);

	if (!success)
		return false;

	this.parentNode.parentNode.removeChild(this.parentNode);
	var option = document.createElement('option');
	option.appendChild(document.createTextNode(value));
	selectli.firstChild.appendChild(option);
	if (selectli.firstChild.disabled)
		selectli.firstChild.disabled = false;

	// Prevent following the link
	return false;
}

function add() {
	// First create the nodes
	var value = this.parentNode.firstChild.value;

	if (value == "---") {
		Log('Please select a group first', false)
		return false;
	}

	// Do the serverside thing!
	var success = addMemberToGroupAjax(value);

	if (!success)
		return false;

	var li = document.createElement('li');
	var link = document.createElement('a');
	link.appendChild(document.createTextNode(value));
	link.href = media_url + '/groups/' + value;
	li.appendChild(link);
	var remover = document.createElement('a');
	remover.className = 'remover';
	remover.onclick = remove;
	remover.href = '#';
	remover.appendChild(document.createTextNode('-'));
	li.appendChild(remover);
	document.getElementById('memberof').insertBefore(li, this.parentNode);

	// Remove the user from the select
	var select = this.parentNode.firstChild;
	select.removeChild(select.options[select.selectedIndex]);
	if (select.options.length == 1)
		select.disabled = true;

	// Prevent following the link
	return false;
}

function selectInit() {
	var groups = document.getElementById('memberof');
	var links = groups.getElementsByTagName('a');
	selectli = document.getElementById('add');
	var map = {'adder': add, 'remover': remove};
	for (var linkidx = 0; linkidx < links.length; ++linkidx) {
		var link = links[linkidx];
		if (!link.className)
			continue;
		link.onclick = map[link.className];
	}

	var select = selectli.firstChild;
	if (select.options.length == 1)
		select.disabled = true;
}
