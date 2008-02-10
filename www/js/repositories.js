load('dom')

// Using window.onload because an onclick="..." handler doesn't give the
// handler a this-variable
var repos_old_load = window.onload;
window.onload = function() {
	if (repos_old_load) repos_old_load();
	setupCollapsables(document.getElementById('content'), 'repostree', null, getsubdirs);
	getsubdirs(document.getElementById('repostree_/'));
}

function getsubdirs(me)
{
	prefix = 'repostree';
	collapsee = collapsables_getCollapsee(prefix, me);
	root = collapsables_getRoot(prefix, collapsee);
	path = root.id.substring(prefix.length + 1, root.id.length);
	if (path != '/')
		path += '/';

	response = AjaxSyncPostRequest(document.location, 'getsubdirs=' + path);
	Log(response.text, response.success);
	dirs = response.xml.getElementsByTagName('dir');
	for (var idx = 0; idx < dirs.length; ++idx) {
		dir = dirs[idx].childNodes[0].nodeValue;
		var has_subdirs = false;
		if (dirs[idx].getAttribute('has_subdirs'))
			has_subdirs = true;

		var new_id = prefix + '_' + path + dir;

		// already added?
		var added = document.getElementById(new_id);
		if (added)
			continue;

		var li = document.createElement('li');
		li.id = new_id;
		li.className = prefix;

		if (has_subdirs) {
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

		collapsee.appendChild(li);
	}
	setupCollapsables(collapsee, prefix, null, getsubdirs);
}

function permissions_update(prefix, triggered)
{
	var li = triggered;
	while (li.nodeName.toLowerCase() != 'li')
		li = li.parentNode;

	path = li.id.substring(prefix.length + 1, li.id.length);

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

