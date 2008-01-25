
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
	setupCollapsables();
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
		img_user.onmousedown = function() { this.src = sidebar_img_add_user_pressed.src; };
		img_user.onmouseout = function() { this.src = sidebar_img_add_user.src; };
	}
	if (img_group) {
		sidebar_img_add_group.src = media_url + '/img/add-group.png';
		sidebar_img_add_group_pressed.src = media_url + '/img/add-group-pressed.png';
		img_group.onmousedown = function() { this.src = sidebar_img_add_group_pressed.src; };
		img_group.onmouseout = function() { this.src = sidebar_img_add_group.src; };
	}
	if (img_repository) {
		sidebar_img_add_repository.src = media_url + '/img/add-repository.png';
		sidebar_img_add_repository_pressed.src = media_url + '/img/add-repository-pressed.png';
		img_repository.onmousedown = function() { this.src = sidebar_img_add_repository_pressed.src; };
		img_repository.onmouseout = function() { this.src = sidebar_img_add_repository.src; };
	}
}

var sidebar_arrow_collapsed = new Image();
var sidebar_arrow_halfway = new Image();
var sidebar_arrow_expanded = new Image();

function setupCollapsables() {
	var collapsables = document.getElementsByTagName('img');

	sidebar_arrow_collapsed.src = media_url + '/img/arrow-collapsed.png';
	sidebar_arrow_halfway.src = media_url + '/img/arrow-halfway.png';
	sidebar_arrow_expanded.src = media_url + '/img/arrow-expanded.png';

	for (var idx = 0; idx < collapsables.length; ++idx) {
		if (collapsables[idx].className == 'collapser') {
			collapsables[idx].onclick = function() { arrowCollapse(this); }
		}
	}
}

function arrowCollapse(image)
{
	// animate image
	image.src = sidebar_arrow_halfway.src;
	setTimeout(function() { image.src = sidebar_arrow_collapsed.src; }, 100);

	// do the collapse
	var collapsable = image.parentNode;
	while (collapsable.className != 'showhide')
		collapsable = collapsable.parentNode;

	var collapsee = collapsable.getElementsByTagName('ul')

	for (var idx = 0; idx < collapsee.length; ++idx)
		collapsee[idx].style.display = 'none';

	// make sure we can expand after this
	image.onclick = function() { arrowExpand(this); }
}

function arrowExpand(image)
{
	// animate image
	image.src = sidebar_arrow_halfway.src;
	setTimeout(function() { image.src = sidebar_arrow_expanded.src; }, 100);

	// do the expand
	var collapsable = image.parentNode;
	while (collapsable.className != 'showhide')
		collapsable = collapsable.parentNode;

	var collapsee = collapsable.getElementsByTagName('ul')

	for (var idx = 0; idx < collapsee.length; ++idx)
		collapsee[idx].style.display = 'inline';

	// make sure we can expand after this
	image.onclick = function() { arrowCollapse(this); }
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
