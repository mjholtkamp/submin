load('dom')
load("selector")
load('ajax')

var selector = null;

function refreshAndLog(response) {
	selector.reInit();
	LogResponse(response);
}

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
	reloadNotifications();
	$('savenotifications').parentNode.onsubmit = saveNotifications;
}

function sendEmail() {
	AjaxAsyncPostLog(document.location, "email=" + $('email').value);
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
	return AjaxAsyncPostRequest(document.location, "addToGroup=" + group, refreshAndLog);
}

function removeMemberFromGroupAjax(group) {
	return AjaxAsyncPostRequest(document.location, "removeFromGroup=" + group, refreshAndLog);
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

function userSelectorInit() {
	selector = new Selector({
			"selectorId": "memberof",
			"urlPrefix": base_url + "groups/show/",
			"initCallback": initGroups,
			"addCallback": addMemberToGroupAjax,
			"removeCallback": removeMemberFromGroupAjax,
			"canLink": function(user) { return is_admin; }
	});
}

function reloadNotifications() {
	AjaxAsyncPostRequest(document.location, "listNotifications", reloadNotificationsCB);
	return false;
}

function reloadNotificationsCB(response) {
	list = FindResponse(response, "listNotifications");
	LogResponse(response);
	
	var notifications = list.xml.getElementsByTagName("notification");
	var n = [];
	for (var i = 0; i < notifications.length; ++i) {
		name = notifications[i].getAttribute('name');
		allowed = notifications[i].getAttribute('allowed');
		enabled = notifications[i].getAttribute('enabled');
		n[n.length] = {"name": name, "allowed": allowed, "enabled": enabled};
	}
	redrawNotifications(n);
}

function redrawNotifications(notifications) {
	var table = document.getElementById('notifications');
	
	for (var item_idx = table.childNodes.length - 1; item_idx > 1; --item_idx)
		table.removeChild(table.childNodes[item_idx]);
	
	for (var i = 0; i < notifications.length; ++i) {
		var tr = $c("tr");
		var td_name = $c("td");
		td_name.appendChild(document.createTextNode(notifications[i].name));
		tr.appendChild(td_name);

		var input = $c("input", {type: "checkbox"});
		if (is_admin) {
			var td_allowed = $c("td");
		
			input.value = notifications[i].name + "_allowed";
			input.checked = (notifications[i].allowed == "True");
			td_allowed.appendChild(input);
			tr.appendChild(td_allowed);

			input = $c("input", {type: "checkbox"});
		}
		input.value = notifications[i].name + "_enabled";
		input.checked = (notifications[i].enabled == "True");

		var td_enabled = $c("td");
		td_enabled.appendChild(input);
		tr.appendChild(td_enabled);
		table.appendChild(tr);
	}
}

function saveNotifications() {
	var table = document.getElementById('notifications');
	
	var str = "";
	for (var item_idx = table.childNodes.length - 1; item_idx > 1; --item_idx) {
		// every childnode (except the first) is a tr. Layout as follows:
		// admin user: <tr><td>repository name</td><td>allowed</td><td>enabled</td></tr>
		// normal user: <tr><td>repository name</td><td>enabled</td></tr>
		var name = table.childNodes[item_idx].childNodes[0].innerHTML;
		var allowed, enabled;

		if (is_admin) {
			allowed = table.childNodes[item_idx].childNodes[1].childNodes[0].checked;
			enabled = table.childNodes[item_idx].childNodes[2].childNodes[0].checked;
		} else {
			allowed = true;
			enabled = table.childNodes[item_idx].childNodes[1].childNodes[0].checked;
		}
		if (str != "")
			str += ":";
			
		str += name + "," + allowed + "," + enabled;
	}

	AjaxAsyncPostRequest(document.location, "saveNotifications=" + str, saveNotificationsCB);
	return false;
}

function saveNotificationsCB(response) {
	list = FindResponse(response, "saveNotifications");
	LogResponse(response);

	reloadNotifications();
}
