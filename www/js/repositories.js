load('dom')

// Using window.onload because an onclick="..." handler doesn't give the
// handler a this-variable
var repos_old_load = window.onload;
window.onload = function() {
	if (repos_old_load) repos_old_load();
	setupCollapsables(document.getElementById('content'), 'repostree', null, getsubdirs);
}

function getsubdirs(me)
{
	prefix = 'repostree';
	collapsee = showhide_getCollapsee(prefix, me);
	root = showhide_getRoot(prefix, collapsee);
	path = root.id.substring(prefix.length + 1, root.id.length);
	response = AjaxSyncPostRequest(document.location, 'getsubdirs=' + path);
	Log(response.text, response.success);
	dirs = response.xml.getElementsByTagName('dir');
	for (var idx = 0; idx < dirs.length; ++idx) {
		dir = dirs[idx].childNodes[0].nodeValue;
		var has_subdirs = false;
		if (dirs[idx].getAttribute('has_subdirs'))
			has_subdirs = true;

		var new_id = prefix + '_' + path + '/' + dir;

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

			li.appendChild(span);
			li.appendChild(folder_img);
			li.appendChild(document.createTextNode(dir));
			li.appendChild(ul);
		} else {
			var folder_img = document.createElement('img');
			folder_img.src = media_url + '/img/repostree-folder.png';
			folder_img.className = "repostree-folder";

			var span = document.createElement('span');
			span.className = 'repostree-noncollapsable';
			span.appendChild(folder_img);
			span.appendChild(document.createTextNode(dir));
			li.appendChild(span);
		}

		collapsee.appendChild(li);
	}
	setupCollapsables(collapsee, prefix, null, getsubdirs);
}

