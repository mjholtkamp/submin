// needs collapsables.js
var sidebar_old_load = window.onload;
window.onload = function() {
	if (sidebar_old_load) sidebar_old_load()

	setupSidebarImages();
	var sidebar = document.getElementById('sidebar');
	setupCollapsables(sidebar, "showhide", sidebar_collapse, sidebar_expand);

	sidebar.onmousedown = function() { return false; }
	sidebar.onselectstart = function() { return false; } // ie
}

function setupSidebarImages() {
	var div_user = document.getElementById('sidebar_add_user');
	var div_group = document.getElementById('sidebar_add_group');
	var div_repository = document.getElementById('sidebar_add_repository');

	// if div is not found (for example if not an admin), don't do anything
	if (div_user) {
		div_user.onmousedown = function() { addClassName(this, "pressed"); return false; };
		div_user.onmouseup = function() { removeClassName(this, "pressed"); };
		div_user.onmouseout = function() { removeClassName(this, "pressed"); };
	}
	if (div_group) {
		div_group.onmousedown = function() { addClassName(this, "pressed"); return false; };
		div_group.onmouseup = function() { removeClassName(this, "pressed"); };
		div_group.onmouseout = function() { removeClassName(this, "pressed"); };
	}
	if (div_repository) {
		div_repository.onmousedown = function() { addClassName(this, "pressed"); return false; };
		div_repository.onmouseup = function() { removeClassName(this, "pressed"); };
		div_repository.onmouseout = function() { removeClassName(this, "pressed"); };
	}
}

function reloadX(response, X, Xplural, Xcapital) {
	var dest = document.getElementById(Xplural);
	if (dest.childNodes)
		for (var i = dest.childNodes.length; i; --i)
			dest.removeChild(dest.lastChild);

	LogResponse(response);
	var list = FindResponse(response, "list" + Xcapital);
	var Xs = list.xml.getElementsByTagName(X);
	// convert into array so we can sort it
	Xs = Array.prototype.slice.call(Xs, 0);
	Xs.sort(xmlSortByName);
	for (var i = 0; i < Xs.length; ++i) {
		var name = Xs[i].getAttribute("name");
		var vcs = Xs[i].getAttribute("vcs");
		var vcs_to_url = "";
		if (vcs)
			vcs_to_url = vcs + "/";

		var status = Xs[i].getAttribute("status");
		if (!status)
			status = "ok";

		var li = $c("li");
		if (selected_type == Xplural && selected_object == name)
			addClassName(li, "selected");

		var link = $c("a", {href: base_url + Xplural + "/show/"
				+ vcs_to_url + name});

		var nameNode = $c("span");
		nameNode.appendChild(document.createTextNode(name));
		link.appendChild(nameNode);

		if (status == "ok") {
			li.appendChild(link);
		} else {
			if (status == "permission denied") {
				nameNode.setAttribute("title", "please check permissions");
				nameNode.setAttribute("class", "err_permission");
			}
			if (status == "wrong version") {
				nameNode.setAttribute("title", "Wrong repository version: please check if python subversion library is up-to-date");
				nameNode.setAttribute("class", "err_version");
			}
			li.appendChild(nameNode);
		}
		if (is_admin && status == "ok") {
			var span = $c("span");
			addClassName(span, "delete" + X);
			span.setAttribute("name", name);
			if (vcs)
				span.setAttribute("vcs", vcs);
			var img = $c("img", {src: base_url + "img/min.png"});
			addClassName(img, "remover");
			span.appendChild(img);
			span.setAttribute("title", "delete " + name)
			span.onclick = deleteObject;
			li.appendChild(span);
		}
		dest.appendChild(li);
	}
}

function reloadUsers(response) {
	reloadX(response, "user", "users", "Users");
}

function reloadGroups(response) {
	reloadX(response, "group", "groups", "Groups");
}

function reloadRepositories(response) {
	reloadX(response, "repository", "repositories", "Repositories");
}

function sidebar_collapse(trigger) {
	var ul = trigger.parentNode.getElementsByTagName("ul")[0];
	if (ul.childNodes)
		for (var i = ul.childNodes.length; i; --i)
			ul.removeChild(ul.lastChild);
}

function sidebar_expand(trigger) {
	var name = trigger.parentNode.getElementsByTagName("ul")[0].id;
	sidebar_reload(name);
}

function sidebar_reload(name) {
	switch (name) {
		case "users":
			AjaxAsyncPostRequest(base_url + 'x', "listUsers", reloadUsers);
			break;
		case "groups":
			AjaxAsyncPostRequest(base_url + 'x', "listGroups", reloadGroups);
			break;
		case "repositories":
			AjaxAsyncPostRequest(base_url + 'x', "listRepositories", reloadRepositories);
			break;
	}
}

function deleteObject()
{
	var div = this.parentNode.parentNode;
	var type = div.id;
	var name = this.getAttribute("name");
	var vcs = this.getAttribute("vcs");
	var vcs_to_url = "";
	if (vcs)
		vcs_to_url = vcs + "/";
	var url = base_url + '' + type + '/delete/' + vcs_to_url + name

	var answer = confirm('Really delete ' + name + '? There is no undo')
	if (!answer)
		return

	var response = AjaxSyncPostRequest(url, "");
	cmd = "";
	switch (type) {
		case "users":        cmd = "removeUser"; break;
		case "groups":       cmd = "removeGroup"; break;
		case "repositories": cmd = "removeRepository"; break; 
	}
	delete_object = FindResponse(response, cmd);
	LogResponse(response);
	if (delete_object && delete_object.success) {
		if (selected_type == div.id && name == selected_object) {
			window.location = base_url + '';
		} else {
			LogResponse(response);
			sidebar_reload(div.id);
		}
	} else {
		LogResponse(response);
	}
}
