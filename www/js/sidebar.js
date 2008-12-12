load('collapsables');

var sidebar_old_load = window.onload;
window.onload = function() {
	if (sidebar_old_load) sidebar_old_load()
	if (!is_admin)
		return;

	setupSidebarImages();
	var sidebar = document.getElementById('sidebar');
	setupCollapsables(sidebar, "showhide", sidebar_collapse, sidebar_expand);

	sidebar.onmousedown = function() { return false; }
	sidebar.onselectstart = function() { return false; } // ie

	 // xml_lists is set in main.html template, fake a response object
	var xml_response = XMLtoResponse(xml_lists);	
	reloadUsers(xml_response);
	reloadGroups(xml_response);
	reloadRepositories(xml_response);
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
		sidebar_img_add_user.src = base_url + 'img/add-user.png';
		sidebar_img_add_user_pressed.src = base_url + 'img/add-user-pressed.png';
		img_user.onmousedown = function() { this.src = sidebar_img_add_user_pressed.src; return false; };
		img_user.onmouseup = function() { this.src = sidebar_img_add_user.src; };
		img_user.onmouseout = function() { this.src = sidebar_img_add_user.src; };
	}
	if (img_group) {
		sidebar_img_add_group.src = base_url + 'img/add-group.png';
		sidebar_img_add_group_pressed.src = base_url + 'img/add-group-pressed.png';
		img_group.onmousedown = function() { this.src = sidebar_img_add_group_pressed.src; return false; };
		img_group.onmouseup = function() { this.src = sidebar_img_add_group.src; };
		img_group.onmouseout = function() { this.src = sidebar_img_add_group.src; };
	}
	if (img_repository) {
		sidebar_img_add_repository.src = base_url + 'img/add-repository.png';
		sidebar_img_add_repository_pressed.src = base_url + 'img/add-repository-pressed.png';
		img_repository.onmousedown = function() { this.src = sidebar_img_add_repository_pressed.src; return false; };
		img_repository.onmouseup = function() { this.src = sidebar_img_add_repository.src; };
		img_repository.onmouseout = function() { this.src = sidebar_img_add_repository.src; };
	}
}

function reloadX(response, X, Xplural, Xcapital) {
	var dest = document.getElementById(Xplural);
	if (dest.childNodes)
		for (var i = dest.childNodes.length; i; --i)
			dest.removeChild(dest.lastChild);

	var list = FindResponse(response, "list" + Xcapital);
	var Xs = list.xml.getElementsByTagName(X);
	for (var i = 0; i < Xs.length; ++i) {
		var name = Xs[i].getAttribute("name");
		var special_group = false;
		// CRUFT after we convert not to abuse submin-admins
		if (X == "group" && name == "submin-admins")
			special_group = true;
		
		var li = $c("li");
		if (selected_type == Xplural && selected_object == name)
			li.setAttribute("class", "selected");

		var link = $c("a", {href: base_url + Xplural + "/show/" + name});

		var nameNode = $c("span");
		nameNode.appendChild(document.createTextNode(name));
		if (special_group) {
			var em = $c("em");
			em.appendChild(nameNode);
			link.appendChild(em);
		} else {
			link.appendChild(nameNode);
		}
		li.appendChild(link);
		if (is_admin && !special_group) {
			var span = $c("span");
			span.setAttribute("class", "delete" + X);
			span.setAttribute("name", name);
			var img = $c("img", {src: base_url + "img/min.gif"});
			img.setAttribute("class", "remover");
			span.appendChild(img);
			span.onclick = deleteObject;
			li.appendChild(span);
		}
		dest.appendChild(li);
		var choplength = parseInt(getStyle(link, "width")) * 0.80;
		var maxlen = autoEllipseText(nameNode, name, choplength);
		nameNode.innerHTML = name.substr(0, maxlen);

		// do we have to chop?
		if (maxlen != name.length) {
			var dotdotdot = $c("span");
			dotdotdot.setAttribute("class", "dotdotdot");
			dotdotdot.appendChild(document.createTextNode("..."));
			link.appendChild(dotdotdot);
			link.setAttribute("title", name);
		}
	}
}

// adapted from http://blog.paranoidferret.com/?p=15
function autoEllipseText(element, text, width)
{
	element.innerHTML = '<span id="ellipsisSpan" style="white-space:nowrap;">' + text + '</span>';
	var inSpan = document.getElementById('ellipsisSpan');
	if (inSpan.offsetWidth > width) {
		var i = 1;
		inSpan.innerHTML = '';
		while (inSpan.offsetWidth < (width) && i <text.length) {
			inSpan.innerHTML = text.substr(0,i) + '...';
			i++;
		} 
		element.innerHTML = '';
		return i;
	}
	return text.length;
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
	var url = base_url + '' + type + '/delete/' + name

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
