// needs dom.js, selector.js and ajax.js (all included in main)

var groupSelector = null;

// Using window.onload because an onclick="..." handler doesn't give the
// handler a this-variable
var old_load = window.onload;
window.onload = function() {
	if (old_load) old_load();
	$('password_button').parentNode.onsubmit = verifyPassword;
	$('email').focus();
	$('is_admin').onclick = setIsAdmin;
	$('ssh_key_add_link').onclick = toggleSSHKeyAddForm;

	var content = document.getElementById('content');
	setupCollapsables(content, "usershowhide", users_collapse, users_expand);

	// Initialize the select-dropdowns
	groupSelectorInit();
	reloadNotifications();
	reloadSSHKeys();
	$('savenotifications').parentNode.onsubmit = saveNotifications;
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
	LogResponse(response);
	reloadNotifications();
}

function sendSendPasswordMail() {
	AjaxAsyncPostLog(document.location, "sendPasswordMail=1");
}

function sendFullName() {
	AjaxAsyncPostLog(document.location, "fullname=" + escape_plus($('fullname').value));
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
	change_password_hint = $('change_password_hint')
	if (change_password_hint) {
		change_password_hint.style.display = 'none';
	}
	return false;
}

function sendPassword(password) {
	AjaxAsyncPostLog(document.location, "password=" + escape_plus(password));
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

function enableRepositoryAjax(repository) {
	var erepository = escape_plus(repository);
	return AjaxAsyncPostRequest(document.location, "setNotification=true&repository=" + erepository);
}

function disableRepositoryAjax(repository) {
	var erepository = escape_plus(repository);
	return AjaxAsyncPostRequest(document.location, "setNotification=false&repository=" + erepository);
}

function groupRefreshAndLog(response) {
	groupSelector.reInit();
	LogResponse(response);
}

function reloadNotifications() {
	AjaxAsyncPostRequest(document.location, "listNotifications", reloadNotificationsCB);
	return false;
}

function reloadNotificationsCB(response) {
	list = FindResponse(response, "listNotifications");
	LogResponse(response);
	
	var notifications = list.xml.getElementsByTagName("notification");
	notifications = Array.prototype.slice.call(notifications, 0);
	notifications.sort(xmlSortByName);
	var n = [];
	for (var i = 0; i < notifications.length; ++i) {
		name = notifications[i].getAttribute('name');
		vcs = notifications[i].getAttribute('vcs');
		enabled = notifications[i].getAttribute('enabled').toLowerCase() == "true";
		n[n.length] = {"name": name, "vcs": vcs, "enabled": enabled};
	}
	redrawNotifications(n);
}

function redrawNotifications(notifications) {
	var table = document.getElementById('notifications');
	var email = document.getElementById('email');
	email = email.value;
	var tbodies = table.getElementsByTagName('tbody');
	if (tbodies.length != 1)
		return;
	var tbody = tbodies[0];
	
	for (var item_idx = tbody.childNodes.length - 1; item_idx > 0; --item_idx)
		tbody.removeChild(tbody.childNodes[item_idx]);
	
	for (var i = 0; i < notifications.length; ++i) {
		var tr = $c("tr");
		var td_name = $c("td");
		var reposname = notifications[i].name;
		var vcs = notifications[i].vcs;
		var a_name = $c("a");
		a_name.appendChild(document.createTextNode(reposname));
		a_name.setAttribute("href", base_url + "repositories/show/" + vcs + "/" + reposname);
		td_name.appendChild(a_name);
		tr.appendChild(td_name);

		// We need to store the repository type somewhere, we use a custom attribute
		tr.setAttribute("data-vcstype", vcs);

		var input = $c("input", {type: "checkbox"});
		input.value = reposname + "_" + vcs + "_enabled";
		input.checked = notifications[i].enabled;
		input.defaultChecked = input.checked; // IE7 quirk
		if (!email || email == "") {
			input.disabled = "disabled";
			input.title = "Please fill in an email address to enable this control";
			input.setAttribute("class", "disabled")
		}

		var td_enabled = $c("td");
		td_enabled.appendChild(input);
		tr.appendChild(td_enabled);
		tbody.appendChild(tr);
	}
}

function saveNotifications() {
	var table = document.getElementById('notifications');
	var tbodies = table.getElementsByTagName('tbody');
	if (tbodies.length != 1)
		return;
	var tbody = tbodies[0];

	var str = "";
	for (var item_idx = tbody.childNodes.length - 1; item_idx > 0; --item_idx) {
		// every childnode is a tr. Layout as follows:
		// <tr><td><a href="...">repository name</a></td><td>enabled</td></tr>
		var tr = tbody.childNodes[item_idx];
		var name = tr.childNodes[0].childNodes[0].innerHTML;
		var vcstype = tr.getAttribute("data-vcstype");
		var enabled = tr.childNodes[1].childNodes[0].checked;
		if (str != "")
			str += "|";

		var ename = escape_plus(name);
		str += vcstype + ":" + ename + "," + enabled;
	}

	// XXX maybe we should use XML here, or even better: JSON
	AjaxAsyncPostRequest(document.location, "saveNotifications=" + str, saveNotificationsCB);
	return false;
}

function saveNotificationsCB(response) {
	list = FindResponse(response, "saveNotifications");
	LogResponse(response);

	reloadNotifications();
}

function toggleSSHKeyAddForm() {
	var ssh_key_parent = $('ssh_key_add_link').parentNode;
	var ssh_key_add_form = $('ssh_key_add_form');
	ssh_key_parent.style.display = ssh_key_parent.style.display == "none" ? "block" : "none";
	ssh_key_add_form.style.display = ssh_key_add_form.style.display == "none" ? "block" : "none";
	if (ssh_key_add_form.style.display != "none")
		$("ssh_key").focus();
	return false;
}

function reloadSSHKeys() {
	AjaxAsyncPostRequest(document.location, "listSSHKeys", reloadSSHKeysCB);
	return false;
}

function reloadSSHKeysCB(response) {
	list = FindResponse(response, "listSSHKeys");
	LogResponse(response);

	var ssh_keys = list.xml.getElementsByTagName("ssh_key");
	var n = [];
	for (var i = 0; i < ssh_keys.length; ++i) {
		id = ssh_keys[i].getAttribute("id");
		title = ssh_keys[i].getAttribute("title");
		key = ssh_keys[i].getAttribute("key");
		n[n.length] = {"id": id, "title": title, "key": key};
	}
	redrawSSHKeys(n);
}

function redrawSSHKeys(ssh_keys) {
	var list = document.getElementById('ssh_keys');

	for (var item_idx = list.childNodes.length - 1; item_idx > 0; --item_idx)
		list.removeChild(list.childNodes[item_idx]);

	for (var i = 0; i < ssh_keys.length; ++i) {
		var li = $c("li");
		li.ssh_key_id = ssh_keys[i].id;

		var a = $c("a", {href: "#"});
		a.appendChild(document.createTextNode(ssh_keys[i].title));
		a.ssh_key = ssh_keys[i].key;
		a.ssh_title = ssh_keys[i].title;
		a.onclick = function() {
			alert("SSH Key `" + this.ssh_title + "':\n" + this.ssh_key);
			return false;
		}
		li.appendChild(a);

		var minus = $c("div", {className: "remover c_icon minus"});
		minus.setAttribute("title", "Delete " + ssh_keys[i].title);
		minus.onclick = removeSSHKey;
		li.appendChild(minus);

		list.appendChild(li);
	}
}

function addSSHKey() {
	post_vars = "addSSHKey=true&title=" + escape_plus($("title").value);
	post_vars += "&ssh_key=" + escape_plus($("ssh_key").value);
	AjaxAsyncPostRequest(document.location, post_vars, addSSHKeyCB);
}

function addSSHKeyCB(response) {
	LogResponse(response);
	if (response[0].success)
	{
		toggleSSHKeyAddForm();
		$("title").value = "";
		$("ssh_key").value = "";

		reloadSSHKeys();
	}
}

function removeSSHKey() {
	AjaxAsyncPostRequest(document.location,
			"removeSSHKey=" + this.parentNode.ssh_key_id,
			removeSSHKeyCB);
}

function removeSSHKeyCB(response) {
	LogResponse(response);
	reloadSSHKeys();
}
