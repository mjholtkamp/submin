load('dom');
load('array');
load('window');

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
}

var repos_old_resize = window.onresize;
window.onresize = function() {
	if (repos_old_resize) repos_old_resize();
	fix_content_div();
}

function resize_content_div()
{
	var content = document.getElementById('content');
	if (!content)
		return;

	var width = WindowWidth() - 200;
	content.style.width = '' + width + 'px';

	var repostree = document.getElementById('repostree');
	var permissions_view = document.getElementById('permissions-view');

	width = width / 2 - 4;

	repostree.style.width = '' + width + 'px';
	permissions_view.style.width = '' + width + 'px';
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
			if (reposnode.path == elem.substring(0, reposnode.path.length)) {
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

function permissions_update(prefix, triggered)
{
	var li = triggered;
	while (li.nodeName.toLowerCase() != 'li')
		li = li.parentNode;

	path = repository_tree.id2path(li.id);

	var permview = document.getElementById('permissions-view');
	var h3 = permview.getElementsByTagName('h3')[0];
	h3.innerHTML = path;

	// first clear list
	var permlist = document.getElementById('permissions-list');
	while (permlist.childNodes.length >= 1)
		permlist.removeChild(permlist.firstChild);

	response = AjaxSyncPostRequest(document.location, 'getpermissions=' + path);
	Log(response.text, response.success);
	perms = response.xml.getElementsByTagName('member');
	for (var idx = 0; idx < perms.length; ++idx) {
		var name = perms[idx].getAttribute('name');
		var perm = perms[idx].getAttribute('permission');

		var label = document.createElement('label');
		label.appendChild(document.createTextNode(name));

		var span = document.createElement('span');
		span.appendChild(document.createTextNode(perm));

		var li = document.createElement('li');
		li.appendChild(label);
		li.appendChild(span);

		permlist.appendChild(li);
	}
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
		span2.onclick = function () { permissions_update(prefix, this); };

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
		span.onclick = function () { permissions_update(prefix, this); };
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

