load('dom');
load('array');
load('window');
load('permeditor');

// for ReposNode object, see below
repository_tree = new ReposNode('repostree');
repository_paths = new Array();

// Using window.onload because an onclick="..." handler doesn't give the
// handler a this-variable
var repos_old_load = window.onload;
window.onload = function() {
	if (repos_old_load) repos_old_load();
	setupCollapsables(document.getElementById('content'), 'repostree', repostree_collapseCB, repostree_expandCB);
	repository_tree.attach('repostree_/');

	repostree_getpaths();
	repostree_expandCB(repository_tree.trigger);
	resize_content_div();
	initPermissionsEditor('/');
}

var repos_old_resize = window.onresize;
window.onresize = function() {
	if (repos_old_resize) repos_old_resize();
	resize_content_div();
}

function resize_content_div()
{
	var content = document.getElementById('content');
	if (!content)
		return;

	var width = WindowWidth() - 200;
	content.style.width = '' + width + 'px';

	var repostree = document.getElementById('repostree');
	var permissions_editor = document.getElementById('permissions-editor');

	width = width / 2 - 4;

	repostree.style.width = '' + width + 'px';
	permissions_editor.style.width = '' + width + 'px';
}

function repostree_getnode(me)
{
	var root = collapsables_getRoot(repository_tree.prefix, me);
	if (!root)
		return null;

	var reposnode = repository_tree.findNodeById(root.id);
	if (!reposnode)
		return null;

	return reposnode;
}

// callback function for when reposnode collapses
function repostree_collapseCB(me)
{
	reposnode = repostree_getnode(me);
	reposnode.collapsed = true;
	repostree_markPermissions(reposnode);
}

// callback function for when reposnode expands
function repostree_expandCB(me)
{
	reposnode = repostree_getnode(me);
	reposnode.collapsed = false;
	getsubdirs(reposnode);
	repostree_markPermissions(reposnode);
}

// mark ReposNodes which have permissions
function repostree_markPermissions(reposnode)
{
	var mark = false;
	for (var idx = 0; idx < repository_paths.length; ++idx) {
		elem = repository_paths[idx];
		if (reposnode.collapsed) {
			if (reposnode.path == elem.substring(0, reposnode.path.length) &&
				elem.charAt(reposnode.path.length) == '/' ||
				reposnode.path == elem) {
				mark = true;
				break;
			}
		} else {
			if (reposnode.path == elem) {
				mark = true;
				break;
			}
		}
	}

	var node;
	if (reposnode.has_subdirs) {
		node = reposnode.root.childNodes[1];
	} else {
		node = reposnode.root.childNodes[0];
	}

	if (mark) {
		addClassName(node, 'has-perms');
	} else {
		removeClassName(node, 'has-perms');
	}

	for (var idx = 0; idx < reposnode.children.length; ++idx)
		repostree_markPermissions(reposnode.children[idx]);
}

function repostree_getpaths()
{
	var response = AjaxSyncPostRequest(document.location, 'getpermissionpaths');

	// log in case there is a problem
	Log(response.text, response.success);

	var permpaths = document.getElementById('permissions-paths');

	// first empty array
	repository_paths.splice(0, repository_paths.length);
	var paths = response.xml.getElementsByTagName('path');
	for (var idx = 0; idx < paths.length; ++idx) {
		var path = paths[idx].getAttribute('name');
		repository_paths.push(path);
	}
}

function getsubdirs(reposnode)
{
	var response = AjaxSyncPostRequest(document.location, 'getsubdirs=' + reposnode.path);

	// log in case there is a problem
	Log(response.text, response.success);

	dirs = response.xml.getElementsByTagName('dir');
	for (var idx = 0; idx < dirs.length; ++idx) {
		dir = dirs[idx].childNodes[0].nodeValue;
		var has_subdirs = false;
		if (dirs[idx].getAttribute('has_subdirs'))
			has_subdirs = true;

		reposnode.createChild(dir, has_subdirs);
	}
	setupCollapsables(reposnode.collapsee, reposnode.prefix, repostree_collapseCB, repostree_expandCB);
}

function reloadPermissions(triggered)
{
	var li = triggered;
	while (li.nodeName.toLowerCase() != 'li')
		li = li.parentNode;

	path = repository_tree.id2path(li.id);

	initPermissionsEditor(path);
}

function loadPermissions(path)
{
	var permview = document.getElementById('permissions-editor');
	var h3 = permview.getElementsByTagName('h3')[0];
	h3.innerHTML = path;

	// get users
	userresponse = AjaxSyncPostRequest(media_url + '/users/', 'list');
	Log(userresponse.text, userresponse.success);
	var addable = new Array()
	users = userresponse.xml.getElementsByTagName('user');
	for (var idx = 0; idx < users.length; ++idx) {
		addable[addable.length] =
			{'type': 'user', 'name': users[idx].getAttribute('name')};
	}

	// get groups as well
	groupresponse = AjaxSyncPostRequest(media_url + '/groups/', 'list');
	Log(groupresponse.text, groupresponse.success);
	groups = groupresponse.xml.getElementsByTagName('group');
	for (var idx = 0; idx < groups.length; ++idx) {
		addable[addable.length] =
			{'type': 'group', 'name': groups[idx].getAttribute('name')};
	}

	addable[addable.length] = {'type': 'user', 'name': '*'}; // for all users

	response = AjaxSyncPostRequest(document.location, 'getpermissions=' + path);
	Log(response.text, response.success);
	perms = response.xml.getElementsByTagName('member');
	var added = [];
	for (var idx = 0; idx < perms.length; ++idx) {
		var name = perms[idx].getAttribute('name');
		var perm = perms[idx].getAttribute('permission');
		var type = perms[idx].getAttribute('type');

		added[added.length] = {"name": name, "permissions": perm, 'type': type};

		for (var addable_idx = 0; addable_idx < addable.length; ++addable_idx) {
			if (addable[addable_idx].name == name &&
				addable[addable_idx].type == type
			) {
				addable.splice(addable_idx, 1);
				break;
			}
		}
	}

	return {'added': added, 'addable': addable};
}

function repostree_reMark(path)
{
	repostree_getpaths();
	var id = 'repostree_' + path;
	var node = repostree_getnode(document.getElementById(id));
	repostree_markPermissions(node);
}

function addPermissionToPath(id, type, path) {
	AjaxSyncPostLog(document.location, 'addpermission&type=' + type + '&name=' + id + '&path=' + path);
	repostree_reMark(path);
}

function removePermissionFromPath(id, type, path) {
	AjaxSyncPostLog(document.location, 'removepermission&type=' + type + '&name=' + id + '&path=' + path);
	repostree_reMark(path);
}

function changePathPermission(id, type, permission, path) {
	AjaxSyncPostLog(document.location, 'setpermission&type=' + type + '&name=' + id + '&path=' + path + '&permission=' + permission);
}

function initPermissionsEditor(path) {
	var permissionsEditor = new PermissionsEditor({
		"editorId": "permissions-list",
		"initCallback": loadPermissions,
		"addCallback": addPermissionToPath,
		"removeCallback": removePermissionFromPath,
		"changeCallback": changePathPermission,
		"path": path
	});
}

//////////////////////////
// ReposNode object
//////////////////////////

function ReposNode(prefix)
{
	this.prefix = prefix;
	this.has_subdirs = false;
	this.collapsed = true;
	this.children = new Array();
}

ReposNode.prototype.id2path = function(id)
{
	var path = id.substring(this.prefix.length + 1, id.length);

	return path;
}

/* Attach this ReposNode to an HTML element with id 'id'
 */
ReposNode.prototype.attach = function(id)
{
	var el = document.getElementById(id);
	this.collapsee = collapsables_getCollapsee(this.prefix, el);
	this.trigger = collapsables_getTrigger(this.prefix, el);
	this.root = collapsables_getRoot(this.prefix, el);
	this.collapsed = collapsables_isCollapsed(this.prefix, el);
	this.path = this.id2path(id);
}

/* Create a new child under ReposNode with subdir name 'dir'
 * and boolean 'has_subdirs'
 */
ReposNode.prototype.createChild = function(dir, has_subdirs)
{
	var path = this.path;
	if (path != '/')
		path += '/';

	var new_id = this.prefix + '_' + path + dir;

	// already added to structure?
	var added = document.getElementById(new_id);
	if (added)
		return;

	newnode = new ReposNode(this.prefix);
	newnode.has_subdirs = has_subdirs;

	// avoid confusion with 'this' in function later on
	var prefix = this.prefix;

	// create HTML elements
	var li = document.createElement('li');
	li.id = new_id;
	li.className = this.prefix;

	if (newnode.has_subdirs) {
		var img = document.createElement('img');
		img.className = prefix + '-icon';
		img.src = media_url + '/img/arrow-collapsed.png';

		var span = document.createElement('span');
		span.className = prefix + '-trigger';
		span.appendChild(img);

		var ul = document.createElement('ul');
		ul.className = prefix + '-object';

		var folder_img = document.createElement('img');
		folder_img.src = media_url + '/img/repostree-folder.png';
		folder_img.className = "repostree-folder";

		var span2 = document.createElement('span');
		span2.appendChild(folder_img);
		span2.appendChild(document.createTextNode(dir));
		span2.onclick = function () { reloadPermissions(this); };

		li.appendChild(span);
		li.appendChild(span2);
		li.appendChild(ul);
	} else {
		var folder_img = document.createElement('img');
		folder_img.src = media_url + '/img/repostree-folder.png';
		folder_img.className = "repostree-folder";

		var span = document.createElement('span');
		span.className = 'repostree-noncollapsable';
		span.appendChild(folder_img);
		span.appendChild(document.createTextNode(dir));
		span.onclick = function () { reloadPermissions(this); };
		li.appendChild(span);
	}

	// attach new HTML to existing HTML
	this.collapsee.appendChild(li);

	// attach new node to HTML
	newnode.attach(new_id);

	// append newnode to our children
	this.children.push(newnode);
}

/* Return ReposNode with a root node with an id of 'id'
 */
ReposNode.prototype.findNodeById = function(id)
{
	if (id == this.root.id)
		return this;

	for (var idx = 0; idx < this.children.length; ++idx) {
		var node = this.children[idx].findNodeById(id);
		if (node)
			return node;
	}

	return null;
}
