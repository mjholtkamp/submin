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
	collapsees = showhide_getCollapsees(prefix, me);
	collapsee = collapsees[0];
	path = collapsee.id.substring(prefix.length + 1, collapsee.id.length);
	response = AjaxSyncPostRequest(document.location, 'getsubdirs=' + path);
	Log(response.text, response.success);
	dirs = response.xml.getElementsByTagName('dir');
	for (var idx = 0; idx < dirs.length; ++idx) {
		dir = dirs[idx].childNodes[0].nodeValue;

		var img = document.createElement('img');
		img.className = prefix + '-icon';
		img.src = media_url + '/img/arrow-expanded.png';

		var span = document.createElement('span');
		span.className = prefix + '-trigger';
		span.appendChild(img);
		span.appendChild(document.createTextNode(dir));

		var ul = document.createElement('ul');
		ul.className = prefix + '-object';
		ul.id = prefix + '_' + path + '/' + dir;

		var li = document.createElement('li');
		li.className = prefix;
		li.appendChild(span);
		li.appendChild(ul);

		collapsee.appendChild(li);
		setupCollapsables(collapsee, prefix, null, getsubdirs);
	}
}

