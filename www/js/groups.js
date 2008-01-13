load('dom')

function removeMemberAjax(member) {
	return AjaxSyncPostLog(document.location, "removeMember=" + member);
}

function addMemberAjax(member) {
	return AjaxSyncPostLog(document.location, "addMember=" + member);
}

var selectli = null;
function remove() {
	var value = this.parentNode.firstChild.firstChild.nodeValue;

	if (value == "---")
		return true;

	// Do the serverside thing!
	var success = removeMemberAjax(value);
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
		Log('Please select a user first', false)
		return false;
	}

	// Do the serverside thing!
	var success = addMemberAjax(value);
	if (!success)
		return false;

	var li = document.createElement('li');
	var link = document.createElement('a');
	link.appendChild(document.createTextNode(value));
	link.href = media_url + '/users/' + value;
	li.appendChild(link);
	var remover = document.createElement('a');
	remover.className = 'remover';
	remover.onclick = remove;
	remover.href = '#';
	var img = document.createElement('img');
	img.className = "remover";
	img.src = media_url + "/img/min.gif";
	remover.appendChild(document.createTextNode(' '));
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
