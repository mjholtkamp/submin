// needs dom.js, selector.js and ajax.js (all included in main)

var groupSelector = null;
var notificationSelector = null;

// Using window.onload because an onclick="..." handler doesn't give the
// handler a this-variable
var old_load = window.onload;
window.onload = function() {
	if (old_load) old_load();
	$('password_button').parentNode.onsubmit = verifyPassword;
	$('email').focus();
	$('is_admin').onclick = setIsAdmin;

	var content = document.getElementById('content');
	setupCollapsables(content, "usershowhide", users_collapse, users_expand);

	// Initialize the select-dropdowns
	groupSelectorInit();
	notificationSelectorInit();
}

function users_collapse(me) {
}

function users_expand(me) {
}

function sendEmail() {
	var eemail = escape_plus($('email').value);
	AjaxAsyncPostRequest(document.location, "email=" + eemail, sendEmailCB);
}

function sendEmailCB(response) {
 	// TODO: Before email is set, notifications are disabled
	notificationRefreshAndLog(response);
}

function sendFullName() {
	AjaxAsyncPostLog(document.location, "fullname=" + $('fullname').value);
}

// global variable to temporarily store the password to be verified
var enteredPassword;
function verifyPassword() {
	var input = $('password');
	enteredPassword = input.value;
	if (!enteredPassword) {
		Log('Please enter a password before pressing "save password"', false);
		return false;
	}

	// Some cleaning up.
	input.value = '';
	this.firstChild.innerHTML = 'Verify';
	// change te onclick handler
	input.focus();
	input.style.background = "lightgreen";
	$('password_button').parentNode.onsubmit = checkPasswords;
	Log('Please verify your password', true);
	return false;
}

function setIsAdmin() {
	// this function is called when the checkbox is already changed.
	// the checkbox reflects the desired (new) value. Don't negate!
	var newvalue = $('is_admin').checked;
	AjaxAsyncPostRequest(document.location, "setIsAdmin=" + newvalue, setIsAdminCB);
}

function setIsAdminCB(response) {
	LogResponse(response);
	var setIsAdmin = FindResponse(response, 'setIsAdmin');
	if (!setIsAdmin.success) {
		$('is_admin').checked = ! $('is_admin').checked;
	}
}

function checkPasswords() {
	// Again some cleaning up.
	this.firstChild.innerHTML = 'Password';
	// Make sure the change-button isn't highlighted anymore
	this.blur();
	// change the onclick handler back to the verifyPassword function
	$('password_button').parentNode.onsubmit = verifyPassword;

	var input = $('password');
	// Do the check after cleaning up.
	if (input.value != enteredPassword) {
		Log('Verification of password failed', false);
		enteredPassword = '';
		input.value = '';
		return false;
	}

	input.style.background = '';
	input.value = '';

	// Send the entered password to the server.
	sendPassword(enteredPassword);
	enteredPassword = '';
	return false;
}

function sendPassword(password) {
	AjaxAsyncPostLog(document.location, "password=" + password);
}


/*
 * Adding users to groups and removing them from groups
 */
function addMemberToGroupAjax(group) {
	var egroup = escape_plus(group);
	return AjaxAsyncPostRequest(document.location, "addToGroup=" + egroup, groupRefreshAndLog);
}

function removeMemberFromGroupAjax(group) {
	var egroup = escape_plus(group);
	return AjaxAsyncPostRequest(document.location, "removeFromGroup=" + egroup, groupRefreshAndLog);
}

/* Requests the groups via ajax, and forms two lists to be used by Selector */
function initGroups() {
	var added = [];
	var addable = [];
	var response = AjaxSyncPostRequest(document.location, 'listUserGroups');
	// log if something went wrong
	LogResponse(response);
	var usergroups = FindResponse(response, 'listUserGroups');
	if (!usergroups)
		return {"added": [], "addable": []};

	var groups = usergroups.xml.getElementsByTagName("group");

	for (var group_idx=0; group_idx < groups.length; ++group_idx) {
		var group = groups[group_idx];
		if (group.getAttribute("member") == "true")
			added[added.length] = group.getAttribute("name");
		else
			addable[addable.length] = group.getAttribute("name");
	}
	return {"added": added, "addable": addable};
}

/* Requests the notifications via ajax, and forms two lists to be used by Selector */
function initNotifications() {
	var added = [];
	var addable = [];
	var response = AjaxSyncPostRequest(document.location, 'listNotifications');
	// log if something went wrong
	LogResponse(response);
	var notificationsresponse = FindResponse(response, 'listNotifications');
	if (!notificationsresponse)
		return {"added": [], "addable": []};

	var notifications = notificationsresponse.xml.getElementsByTagName("notification");

	for (var n_idx=0; n_idx < notifications.length; ++n_idx) {
		var notification = notifications[n_idx];
		if (notification.getAttribute("enabled").toLowerCase() == "true")
			added[added.length] = notification.getAttribute("name");
		else
			addable[addable.length] = notification.getAttribute("name");
	}
	return {"added": added, "addable": addable};
}

function groupSelectorInit() {
	groupSelector = new Selector({
			"selectorId": "memberof",
			"urlPrefix": base_url + "groups/show/",
			"initCallback": initGroups,
			"addCallback": addMemberToGroupAjax,
			"removeCallback": removeMemberFromGroupAjax,
			"canLink": function(user) { return true; },
			"canEdit": function() { return is_admin; }
	});
}

function notificationSelectorInit() {
	notificationSelector = new Selector({
			"selectorId": "notifications",
			"urlPrefix": base_url + "repositories/show/",
			"initCallback": initNotifications,
			"addCallback": enableRepositoryAjax,
			"removeCallback": disableRepositoryAjax,
			"canLink": function(user) { return true; },
			"canEdit": function() { return true; }
	});
}


function enableRepositoryAjax(repository) {
	var erepository = escape_plus(repository);
	return AjaxAsyncPostRequest(document.location, "setNotification=true&repository=" + erepository, notificationRefreshAndLog);
}

function disableRepositoryAjax(repository) {
	var erepository = escape_plus(repository);
	return AjaxAsyncPostRequest(document.location, "setNotification=false&repository=" + erepository, notificationRefreshAndLog);
}

function groupRefreshAndLog(response) {
	groupSelector.reInit();
	LogResponse(response);
}

function notificationRefreshAndLog(response) {
	notificationSelector.reInit();
	LogResponse(response);
}
