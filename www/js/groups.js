load('dom')

function removeMemberAjax(member) {
	return AjaxSyncPostLog(document.location, "removeMember=" + member);
}

function addMemberAjax(member) {
	return AjaxSyncPostLog(document.location, "addMember=" + member);
}

var selectli = null;
function remove() {
	var li = this.parentNode;
	var username = li.id.replace('user.', '');

	if (username == "---")
		return true;

	// Do the serverside thing!
	var success = removeMemberAjax(username);
	if (!success)
		return false;

	this.parentNode.parentNode.removeChild(this.parentNode);
	var option = document.createElement('option');
	option.appendChild(document.createTextNode(username));
	selectli.firstChild.appendChild(option);
	if (selectli.firstChild.disabled)
		selectli.firstChild.disabled = false;

	// Prevent following the link
	return false;
}

function add() {
	// First create the nodes
	var username = this.parentNode.firstChild.value;

	if (username == "---") {
		Log('Please select a user first', false)
		return false;
	}

	// Do the serverside thing!
	var success = addMemberAjax(username);
	if (!success)
		return false;

	var li = document.createElement('li');
	li.id = 'user.' + username;
	var link = document.createElement('a');
	link.appendChild(document.createTextNode(username));
	link.href = media_url + '/users/show/' + username;
	li.appendChild(link);
	var remover = document.createElement('a');
	remover.className = 'remover';
	remover.onclick = remove;
	remover.href = '#';
	var img = document.createElement('img');
	img.className = "remover";
	img.src = media_url + "/img/min.gif";
	remover.appendChild(img);
	li.appendChild(remover);
	document.getElementById('members').insertBefore(li, this.parentNode);

	// Remove the user from the select
	var select = this.parentNode.firstChild;
	select.removeChild(select.options[select.selectedIndex]);
	if (select.options.length == 1)
		select.disabled = true;

	// Prevent following the link
	return false;
}

var old_load = window.onload;
window.onload = function() {
	if (old_load) old_load();
	var groups = document.getElementById('members');
	var links = groups.getElementsByTagName('a');
	selectli = document.getElementById('add');

	// user might be a non-admin, then no selectli exists
	if (!selectli)
		return;

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
