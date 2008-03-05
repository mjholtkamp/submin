load('dom')
load("selector")

// Using window.onload because an onclick="..." handler doesn't give the
// handler a this-variable
var old_load = window.onload;
window.onload = function() {
	if (old_load) old_load();
	$('password_button').parentNode.onsubmit = verifyPassword;
	$('email').focus();

	// Initialize the select-dropdown
	//selectInit();
	userSelectorInit();
}

function sendEmail() {
	AjaxAsyncPostLog(document.location, "email=" + $('email').value);
}

// global variable to temporarily store the password to be verified
var enteredPassword;
function verifyPassword() {
	var input = $('password')
	enteredPassword = input.value;
	if (!enteredPassword) {
		Log('Please enter a password before pressing "change"', false);
		return false;
	}

	// Some cleaning up.
	input.value = '';
	this.firstChild.innerHTML = 'Verify';
	// change te onclick handler
	input.focus();
	$('password_button').parentNode.onsubmit = checkPasswords;
	Log('Please verify your password', true);
	return false;
}

function checkPasswords() {
	// Again some cleaning up.
	this.firstChild.innerHTML = 'Password';
	// Make sure the change-button isn't highlighted anymore
	this.blur();
	// change the onclick handler back to the verifyPassword function
	$('password_button').parentNode.onsubmit = verifyPassword;

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
	AjaxAsyncPostLog(document.location, "password=" + password)
}


/*
 * Adding users to groups and removing them from groups
 */
function addMemberToGroupAjax(group) {
	return AjaxAsyncPostLog(document.location, "addToGroup=" + group);
}

function removeMemberFromGroupAjax(group) {
	return AjaxAsyncPostLog(document.location, "removeFromGroup=" + group);
}

/* Requests the groups via ajax, and forms two lists to be used by Selector */
function initGroups() {
	var added = [];
	var addable = [];
	var response = AjaxSyncPostRequest(document.location, 'initSelector=1');
	var groups = response.xml.getElementsByTagName("group");
	Log(response.text, response.success);

	for (var group_idx=0; group_idx < groups.length; ++group_idx) {
		var group = groups[group_idx];
		if (group.getAttribute("member") == "true")
			added[added.length] = group.getAttribute("name");
		else
			addable[addable.length] = group.getAttribute("name");
	}
	return {"added": added, "addable": addable};
}

function userSelectorInit() {
	var selector = new Selector({
			"selectorId": "memberof",
			"urlPrefix": base_url + "/groups/show/",
			"init": initGroups,
			"addCallback": addMemberToGroupAjax,
			"removeCallback": removeMemberFromGroupAjax,
			"canLink": function(user) { return is_admin; }
	});
}
