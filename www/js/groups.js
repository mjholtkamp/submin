// check if basic.js is loaded, for including of dependencies
if (typeof basicLoaded == 'undefined') {
	alert('This script requires basic.js. Please add <script src="basic.js" type="text/javascript"></script> to the <head> section of your document.');
}
	
load('array');
load('dom');

function initGroups() {
	var groups = $('groups');
	var groupDivs = $$(groups, 'div', 'groups');
	for (var i=0; i<groupDivs.length; i++) {
		$$(byTag(groupDivs[i], 'span'), 'a', 'addToGroup')[0].onclick = addToGroup;
		$$(byTag(groupDivs[i], 'span'), 'a', 'expand')[0].onclick = expandMembers;
	}
}

var Groups = {
	groupContainer: 'groups',
	groups: [],
	handlers: {},
	add: function(group) {
		this.groups[this.groups.length] = group;
	},
	each: function(iterator) {
		for (var i=0; i<this.groups.length; i++) {
			iterator(this.groups[i]);
		}
	},
	create: function() {
		this.each(function(group){group.create()})
	},
	byGroupname: function(groupname) {
		for (var i=0; i<this.groups.length; i++) {
			if (this.groups[i].groupname == groupname)
				return this.groups[i];
		}
		return null;
	},
	expandAll: function() {
		this.each(function(group){group.expand()});
	},
	collapseAll: function() {
		this.each(function(group){group.collapse()});
	}
}

function Group(groupname, members) {
	this.groupname = groupname;
	this.expanded = false;
	
	var tmembers = [];
	if (typeof members.length != 'undefined') {
		// members is an array
		members.each(function(user) {
			if (typeof user == 'string')
				tmembers[tmembers.length] = Users.byUsername(user);
			else
				tmembers[tmembers.length] = user;
		});
	}
	this.members = tmembers;
	
	// Register event handlers for Users.
	Users.registerEventHandler('select', this, 'showHideButton');
	Users.registerEventHandler('unselect', this, 'showHideButton');
	
	Groups.add(this);
	
	if ($(Groups.groupContainer))
		this.create();
}

/* Creates the HTML elements for the group */
Group.prototype.create = function() {
	// The html for a group:
	// <div class="groups" id="submerge"><span><a href="#" class="expand"><img src="img/pijltje-right.jpg" alt="" /></a> Submerge <a href="#" class="addToGroup" style="display: none"><img src="img/addtogroup.jpg" alt="" /></a></span>
	//	<div id="submergemembers" class="members" style="display:none"></div>
	// </div>
	this.div = $c('div', {className: 'groups', id: this.groupname});
	this.span = $c('span');
	// TODO: Why have a expand anchor? Just fix the image's style and onclick handler.
	this.aExpand = $c('a', {href: '#', className: 'expand'});
	this.arrow = $c('img', {src: 'img/pijltje-right.jpg'});
	this.aExpand.appendChild(this.arrow);
	this.span.appendChild(this.aExpand);
	this.span.appendChild(document.createTextNode(" " + this.groupname + " "));
	
	var _this = this;
	this.aExpand.onclick = function() {
		Groups.byGroupname(this.parentNode.parentNode.id).expandToggle();
		this.blur();
		return false; // prevent following the link.
	}
	
	// TODO: Why have a aAddToGroup? Just fix the image's style and onclick handler.
	this.aAddToGroup = $c('a', {href: '#', className: 'addToGroup', style: {display: 'none'}});
	this.iAddToGroup = $c('img', {src: 'img/addtogroup.jpg'});
	this.aAddToGroup.appendChild(this.iAddToGroup);
	
	var _this = this;
	this.aAddToGroup.onclick = function(e) {
		Groups.byGroupname(this.parentNode.parentNode.id).addSelectedUsers();
		_this.memberul.size = _this.members.length;
		this.blur();
		return false; // prevent following the link.
	};
	
	this.span.appendChild(this.aAddToGroup);

	this.users_small = $c('small', {className: 'users'});
	user_txt = '';
	for (var i=0; i<Math.min(3, this.members.length); i++) {
		if (i != 0) user_txt += ', ';
		user_txt += this.members[i].username;
	}
	if (this.members.length > 3)
		user_txt += '...';
	this.users_small.appendChild(document.createTextNode(user_txt))
	this.span.appendChild(this.users_small)


	this.div.appendChild(this.span);
	
	this.memberdiv = $c('div', {className: 'members', style: {display: 'none'}});
	memberul = $c('select', {multiple: 'multiple', size: this.members.length});
	this.members.each(function(user){
		// this could be more elaborate, but this is enough for now :)
		var member = $c('option', {innerHTML: user.username});
		memberul.appendChild(member);
	});
	this.memberul = memberul;
	this.memberdiv.appendChild(this.memberul);
	this.div.appendChild(this.memberdiv);
	
	$(Groups.groupContainer).appendChild(this.div);
	
	return this.div;
}

Group.prototype.expand = function() {
	this.expanded = true;
	Element.show(this.memberdiv);
	addClassName(this.div, 'expanded');
	this.arrow.src = 'img/pijltje-down.jpg';
}

Group.prototype.collapse = function() {
	this.expanded = false;
	Element.hide(this.memberdiv);
	removeClassName(this.div, 'expanded');
	this.arrow.src = 'img/pijltje-right.jpg';
}

Group.prototype.expandToggle = function() {
	if (this.expanded)
		this.collapse();
	else
		this.expand();
}

Group.prototype.showButton = function() {
	Element.show(this.aAddToGroup);
}

Group.prototype.hideButton = function() {
	Element.hide(this.aAddToGroup);
}

Group.prototype.showHideButton = function(users) {
	// Shows or hides the add to group button
	if (users.selectedUsers.length)
		this.showButton();
	else
		this.hideButton();
}

Group.prototype.addSelectedUsers = function() {
	if (!Users.selectedUsers.length)
		return;
	
	// Do not write as Users.selectedUsers.each(); because we have to create 
	// a local variable for members and memberul.
	for(var a=Users.selectedUsers,i=a.iter(); a.hasNext(); i=a.next()) {
		if (this.members.member(i))
			continue;
		this.memberul.appendChild($c('option', {innerHTML:i.username}));
		this.members.push(i);
	}
}

function addToGroup() {
	if (!Users.selectedUsers.length) 
		return;
		
	var parent = this.parentNode.parentNode;

	if (doNotAdd == parent.id) {
		doNotAdd = null;
		return;
	}

	var txt = '';
	for (var i=0; i<Users.selectedUsers.length; i++)
		txt += Users.selectedUsers[i].username + "<br />";
	$$(parent, 'div', 'members')[0].innerHTML = txt;
	
	return false;
}

function expandMembers() {
	$$(this.parentNode.parentNode, 'div', 'members')[0].style.display = '';
	addClassName(this.parentNode.parentNode, 'expanded');
	this.onclick = hideMembers;
	byTag(this, 'img').src = 'img/pijltje-down.jpg';
	this.blur();
	return false; // prevent using link
}

function hideMembers() {
	$$(this.parentNode.parentNode, 'div', 'members')[0].style.display = 'none';
	removeClassName(this.parentNode.parentNode, 'expanded');
	this.onclick = expandMembers;
	byTag(this, 'img').src = 'img/pijltje-right.jpg';
	this.blur();
	return false; // prevent using link
}


function showAllAddButtons() {
	var groups = $('groups');
	var groupDivs = $$(groups, 'div', 'groups');
	for (var i=0; i<groupDivs.length; i++) {
		$$(byTag(groupDivs[i], 'span'), 'a', 'addToGroup')[0].style.display = '';
	}
}

function hideAllAddButtons() {
	var groups = $('groups');
	var groupDivs = $$(groups, 'div', 'groups');
	for (var i=0; i<groupDivs.length; i++) {
		$$(byTag(groupDivs[i], 'span'), 'a', 'addToGroup')[0].style.display = 'none';
	}
}


registerLoadFunction(function(){Groups.create();Groups.expandAll()});
