load('collapsables');

var sidebar_old_load = window.onload;
window.onload = function() {
	if (sidebar_old_load) sidebar_old_load()
	var users = document.getElementById('users')
	var groups = document.getElementById('groups')
	var deleters = users.getElementsByTagName('span')

	for (var idx = 0; idx < deleters.length; ++idx) {
		var deleter = deleters[idx]
		deleter.onclick = deleteObject
	}

	deleters = groups.getElementsByTagName('span')

	for (var idx = 0; idx < deleters.length; ++idx) {
		var deleter = deleters[idx]
		deleter.onclick = deleteObject
	}

	setupSidebarImages();
	setupCollapsables(document.body, "showhide");
}

var sidebar_img_add_user = new Image();
var sidebar_img_add_group = new Image();
var sidebar_img_add_repository = new Image();
var sidebar_img_add_user_pressed = new Image();
var sidebar_img_add_group_pressed = new Image();
var sidebar_img_add_repository_pressed = new Image();

function setupSidebarImages() {
	var img_user = document.getElementById('sidebar_add_user_img');
	var img_group = document.getElementById('sidebar_add_group_img');
	var img_repository = document.getElementById('sidebar_add_repository_img');

	// if image is not found (for example if not an admin), don't do anything
	if (img_user) {
		sidebar_img_add_user.src = media_url + '/img/add-user.png';
		sidebar_img_add_user_pressed.src = media_url + '/img/add-user-pressed.png';
		img_user.onmousedown = function() { this.src = sidebar_img_add_user_pressed.src; return false; };
		img_user.onmouseup = function() { this.src = sidebar_img_add_user.src; };
		img_user.onmouseout = function() { this.src = sidebar_img_add_user.src; };
	}
	if (img_group) {
		sidebar_img_add_group.src = media_url + '/img/add-group.png';
		sidebar_img_add_group_pressed.src = media_url + '/img/add-group-pressed.png';
		img_group.onmousedown = function() { this.src = sidebar_img_add_group_pressed.src; return false; };
		img_group.onmouseup = function() { this.src = sidebar_img_add_group.src; };
		img_group.onmouseout = function() { this.src = sidebar_img_add_group.src; };
	}
	if (img_repository) {
		sidebar_img_add_repository.src = media_url + '/img/add-repository.png';
		sidebar_img_add_repository_pressed.src = media_url + '/img/add-repository-pressed.png';
		img_repository.onmousedown = function() { this.src = sidebar_img_add_repository_pressed.src; return false; };
		img_repository.onmouseup = function() { this.src = sidebar_img_add_repository.src; };
		img_repository.onmouseout = function() { this.src = sidebar_img_add_repository.src; };
	}
}

function deleteObject()
{
	var div = this.parentNode.parentNode
	var type = ''
	switch (div.id) {
		case 'users':
		case 'groups':
			type = div.id
			break
		default:
			return
			break
	}
	var name = this.parentNode.firstChild.firstChild.nodeValue;
	var url = media_url + '/' + type + '/delete/' + name

	var answer = confirm('Really delete ' + name + '? There is no undo')
	if (!answer)
		return

	var response = AjaxSyncPostRequest(url, "")
	Log(response.text, response.success)
	if (response.success)
		this.parentNode.parentNode.removeChild(this.parentNode)

	if (selected_type == div.id && name == selected_object)
		window.location = media_url + '/';
}
