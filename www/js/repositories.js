load('dom');
load('array');
load('window');
load('selector');

// for ReposNode object, see below
var repository_tree = new ReposNode('repostree');
var repository_paths = new Array();
var permissionsEditor = null;

// do this before window.onload
function beforeLoad() {
	repostree_getpaths();
}
beforeLoad();

// Using window.onload because an onclick="..." handler doesn't give the
// handler a this-variable
var repos_old_load = window.onload;
window.onload = function() {
	if (repos_old_load) repos_old_load();
	setupCollapsables(document.getElementById('content'), 'repostree', repostree_collapseCB, repostree_expandCB);
	repository_tree.attach('repostree_/');
	document.getElementById('repostree_root_text').onclick = function() {
		reloadPermissions(this);
	};

	repostree_expandCB(repository_tree.trigger);
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
	content.style.width = width + 'px';

	var repostree = document.getElementById('repostree');
	var permissions_editor = document.getElementById('permissions-editor');

	width = width / 2 - 24;

	repostree.style.width = width + 'px';
	permissions_editor.style.width = width + 'px';
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
	var reposnode = repostree_getnode(me);
	reposnode.collapsed = true;
	repostree_markPermissions(reposnode);
}

// callback function for when reposnode expands
function repostree_expandCB(me)
{
	var reposnode = repostree_getnode(me);
	reposnode.collapsed = false;
	getsubdirs(reposnode);
	repostree_markPermissions(reposnode);
}

// mark ReposNodes which have permissions
function repostree_markPermissions(reposnode)
{
	var mark = false;
	var rep_path_length = repository_paths.length;
	var collapsed = reposnode.collapsed;
	var path = reposnode.path;
	for (var idx = 0; idx < rep_path_length; ++idx) {
		var elem = repository_paths[idx];
		if (collapsed) {
			if (path == elem.substring(0, path.length) &&
				elem.charAt(path.length) == '/' ||
				path == elem) {
				mark = true;
				break;
			}
		} else {
			if (path == elem) {
				mark = true;
				break;
			}
		}
	}

	var node;
	if (path == '/') {
		node = document.getElementById('repostree_root_text');
	} else if (reposnode.has_subdirs) {
		node = reposnode.root.childNodes[1];
	} else {
		node = reposnode.root.childNodes[0];
	}

	if (mark) {
		addClassName(node, 'has-perms');
	} else {
		removeClassName(node, 'has-perms');
	}

	var rep_children_len = reposnode.children.length;
	var children = reposnode.children;
	for (var idx = 0; idx < rep_children_len; ++idx)
		repostree_markPermissions(children[idx]);
}

function repostree_getpaths()
{
	var response = AjaxSyncPostRequest(document.location, 'getPermissionPaths');

	// log in case there is a problem
	LogResponse(response);
	
	permissionspaths = FindResponse(response, 'getPermissionPaths');

	// first empty array
	repository_paths.splice(0, repository_paths.length);
	var paths = permissionspaths.xml.getElementsByTagName('path');
	var paths_length = paths.length;
	for (var idx = 0; idx < paths_length; ++idx) {
		var path = paths[idx].getAttribute('name');
		repository_paths.push(path);
	}
}

function getsubdirs(reposnode)
{
	var response = AjaxSyncPostRequest(document.location, 'getSubdirs=' + reposnode.path);

	// log in case there is a problem
	LogResponse(response);
	var subdirs = FindResponse(response, 'getSubdirs');

	var dirs = subdirs.xml.getElementsByTagName('dir');
	var dirs_length = dirs.length;
	for (var idx = 0; idx < dirs_length; ++idx) {
		var dir = dirs[idx];
		var dirname = dir.childNodes[0].nodeValue;
		var has_subdirs = false;
		if (dir.getAttribute('has_subdirs') == 'True')
			has_subdirs = true;

		reposnode.createChild(dirname, has_subdirs);
	}
	setupCollapsables(reposnode.collapsee, reposnode.prefix, repostree_collapseCB, repostree_expandCB);
}

function reloadPermissions(triggered)
{
	var li = triggered;
	while (li.nodeName.toLowerCase() != 'li')
		li = li.parentNode;

	var path = repository_tree.id2path(li.id);

	initPermissionsEditor(path);
}

function loadPermissions(path)
{
	var permview = document.getElementById('permissions-editor');
	var h3 = permview.getElementsByTagName('h3')[0];
	h3.innerHTML = path;

	// get permissions, users and groups in one call
	var response = AjaxSyncPostRequest(document.location, 'getPermissions=' + path + '&userlist&grouplist');
	LogResponse(response);

	repositoryperms = FindResponse(response, "getRepositoryPerms");

	// process users
	var addable = new Array();
	var users = repositoryperms.xml.getElementsByTagName('user');
	var users_length = users.length;
	for (var idx = 0; idx < users_length; ++idx) {
		addable[addable.length] =
			{'type': 'user', 'name': users[idx].getAttribute('name')};
	}

	// process groups
	var groups = repositoryperms.xml.getElementsByTagName('group');
	var groups_length = groups.length;
	for (var idx = 0; idx < groups_length; ++idx) {
		addable[addable.length] =
			{'type': 'group', 'name': groups[idx].getAttribute('name')};
	}

	addable[addable.length] = {'type': 'user', 'name': '*'}; // for all users

	// process permissions
	var perms = repositoryperms.xml.getElementsByTagName('member');
	var perms_length = perms.length;
	var added = [];
	for (var idx = 0; idx < perms_length; ++idx) {
		var perm = perms[idx];
		var name = perm.getAttribute('name');
		var permission = perm.getAttribute('permission');
		var type = perm.getAttribute('type');

		added[added.length] = {"name": name, "permissions": permission, 'type': type};

		var addable_length = addable.length;
		for (var addable_idx = 0; addable_idx < addable_length; ++addable_idx) {
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

function repostree_reMark(response, path)
{
	LogResponse(response);
	repostree_getpaths();
	var id = 'repostree_' + path;
	var node = repostree_getnode(document.getElementById(id));
	repostree_markPermissions(node);
	permissionsEditor.reInit();
}

function refreshAndLog(response) {
	permissionsEditor.reInit();
	LogResponse(response);
}

function addPermissionToPath(id, type, path) {
	AjaxAsyncPostRequest(document.location, 'addPermission&type=' + type + '&name=' + id + '&path=' + path, function(response) { repostree_reMark(response, path); } );
}

function removePermissionFromPath(id, type, path) {
	AjaxAsyncPostRequest(document.location, 'removePermission&type=' + type + '&name=' + id + '&path=' + path, function(response) { repostree_reMark(response, path); } );
}

function changePathPermission(id, type, permission, path) {
	AjaxAsyncPostRequest(document.location, 'setPermission&type=' + type + '&name=' + id + '&path=' + path + '&permission=' + permission, refreshAndLog);
}

function initPermissionsEditor(path) {
	if (permissionsEditor)
		permissionsEditor.destroy();

	permissionsEditor = new Selector({
		"type": "permissions",
		"selectorId": "permissions-list",
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
	return id.substring(this.prefix.length + 1, id.length);
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

	var newnode = new ReposNode(this.prefix);
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
		img.src = base_url + 'img/arrow-collapsed.png';

		var span = document.createElement('span');
		span.className = prefix + '-trigger';
		span.appendChild(img);

		var ul = document.createElement('ul');
		ul.className = prefix + '-object';

		var folder_img = document.createElement('img');
		folder_img.src = base_url + 'img/repostree-folder.png';
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
		folder_img.src = base_url + 'img/repostree-folder.png';
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

/* ask server to re-enable post-commit hook, this is called from an anchor */
function toggle_notifications_mailing() {
	AjaxAsyncPostLog(document.location, 'toggleNotifications');
	return false; // no following of link
}
