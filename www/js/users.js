var doNotAdd = null;

// check if basic.js is loaded, for including of dependencies
if (typeof basicLoaded == 'undefined') {
	alert('This script requires basic.js. Please add <script src="basic.js" type="text/javascript"></script> to the <head> section of your document.');
}
	
load('array');
load('dom');

/* Singleton that contains all the users and functions that operate on the whole set.
 * Also contains the selected users.
 */
var Users = {
	userContainer: 'users',
	users: [],
	selectedUsers: [],
	doNotSelect: null, // this is to prevent selecting a user when expanding it through it's arrow.
	handlers: {},
	add: function(user) {
		this.users[this.users.length] = user;
		return user;
	},
	each: function(iterator) {
		for (var i=0; i<this.users.length; i++)
			iterator(this.users[i]);
	},
	create: function() {
		this.each(function(user){user.create()})
	},
	byUsername: function(username) {
		for (var i=0; i<this.users.length; i++) {
			if (this.users[i].username == username)
				return this.users[i];
		}
		return null;
	},
	collapseAll: function() {
		this.each(function(user){user.collapse()})
	},
	expandAll: function() {
		this.each(function(user){user.expand()})
	},
	selectNone: function() {
		this.each(function(user){user.unselect()})
	},
	selectAll: function() {
		this.each(function(user){user.select()})
	},
	invertSelection: function() {
		this.each(function(user){user.selectToggle()})
	},
	registerEventHandler: function(event, obj, func) {
		if (typeof this.handlers[event] == 'undefined')
			this.handlers[event] = [];
		this.handlers[event].push([obj, func]);
	},
	triggerEvent: function(event) {
		if (typeof this.handlers[event] == 'undefined' || !this.handlers[event].length)
			return
		for (var i=0; i<this.handlers[event].length; i++) {
			var cur = this.handlers[event][i];
			var obj = cur[0];
			var func = cur[1];
			obj[func](this);
		}
	}
}

/* Class Users; manages a single user */
function User(username, email) {
	this.username = username;
	this.email = email;
	
	this.selected = false;
	this.expanded = false;
	
	Users.add(this);
	
	if ($(Users.userContainer))
		this.create();
}


/* returns a div-HTMLElement */
User.prototype.create = function() {
	this.div = $c('div', {className: 'users', id: this.username})
	this.div.appendChild(this.createHead());
	this.div.appendChild(this.createSettings());
	
	$(Users.userContainer).appendChild(this.div);
		
	return this.div;
}

/* Returns a div-HTMLElement; creates the head of the user-block */
User.prototype.createHead = function() {
/*	var span = document.createElement('span');*/
	this.span = $c('span');
	this.a = $c('a', {href:'#', className: 'addToGroup'})
	this.arrow = $c('img', {src: 'img/pijltje-right.jpg'})
	
	this.a.appendChild(this.arrow);
	
	this.a.onclick = function() {
		Users.doNotSelect = this.parentNode.parentNode.id;

		Users.byUsername(this.parentNode.parentNode.id).expandToggle();
		this.blur();
		return false; // prevent using link
	};
	
	this.span.appendChild(this.a);
	
	this.span.appendChild(document.createTextNode(" " + this.username + " "));
	
	this.small = $c('small', {innerHTML: '&lt;' + this.email + '&gt;'})
	this.span.appendChild(this.small);
	this.span.onclick = function() {
		Users.byUsername(this.parentNode.id).selectToggle()
	};
	
	return this.span;
}

/* Returns a div-HTMLElement; creates the settings-part of the user-block */
User.prototype.createSettings = function() {
	this.settingsDiv = $c('div', {className: 'settings', style: {display: 'none'}})
	this.settingsUl = $c('ul');
	
	var fields = [
		{label:'Password', type:'password', name:'password_' + this.username, value:''},
		{label:'E-mailaddress', type:'text', name:'email_' + this.username, value:this.email}
	];
	
	for (var i=0;i<fields.length;i++) {
		var cur = fields[i];
		var li = $c('li');
		var label = $c('label', {htmlFor:cur.name,innerHTML:cur.label});
		var input = $c('input', {type:cur.type, name:cur.name, id:cur.name, value:cur.value});
		li.appendChild(label);
		li.appendChild(input);
		this.settingsUl.appendChild(li);
	}
	this.settingsDiv.appendChild(this.settingsUl);
	return this.settingsDiv;
}

/* Expands a user-block with its settings. */
User.prototype.expand = function() {
	if (this.expanded)
		return;
	this.expanded = true;
	this.settingsDiv.style.display = '';
	addClassName(this.div, 'expanded');
	
	var src = 'img/pijltje-down.jpg';
	if (this.selected)
		src = 'img/pijltje-selected-down.jpg';
		
	this.arrow.src = src;
	Users.triggerEvent('expand');
}

/* Collapses a user-blocks settings. */
User.prototype.collapse = function() {
	if (!this.expanded)
		return;
		
	this.expanded = false;
	
	this.settingsDiv.style.display = 'none';
	removeClassName(this.div, 'expanded');
	
	var src = 'img/pijltje-right.jpg';
	if (this.selected)
		src = 'img/pijltje-selected-right.jpg';
		
	this.arrow.src = src;
	Users.triggerEvent('collapse');
}

/* Toggle the expanded state of the users-settings */
User.prototype.expandToggle = function() {
	if (this.expanded)
		this.collapse()
	else
		this.expand()
}

/* Select the user and adjust the user-blocks style */
User.prototype.select = function() {
	if (this.selected)
		return;
		
	if (Users.doNotSelect == this.username) {
		Users.doNotSelect = null;
		return;
	}
	
	this.selected = true;
	
	var src = 'img/pijltje-';

	addClassName(this.div, 'selected');
	Users.selectedUsers.push(this);
	src += 'selected-';
	
	if (this.expanded)
		src += "down.jpg"
	else
		src += "right.jpg";
	
	this.arrow.src = src
	
	Users.triggerEvent('select');
	
	if (Users.selectedUsers.length) {
		showAllAddButtons();
	} else {
		hideAllAddButtons();
	}
}

/* Unselect the user and adjust the user-blocks style */
User.prototype.unselect = function() {
	if (!this.selected)
		return;
		
	if (Users.doNotSelect == this.username) {
		Users.doNotSelect = null;
		return;
	}
	
	this.selected = false;
	
	var src = 'img/pijltje-';

	removeClassName(this.div, 'selected');
	Users.selectedUsers.del(this);
	src += '';
	
	if (this.expanded)
		src += "down.jpg"
	else
		src += "right.jpg";
	
	this.arrow.src = src
	
	Users.triggerEvent('unselect');
	
	if (Users.selectedUsers.length) {
		showAllAddButtons();
	} else {
		hideAllAddButtons();
	}
}

/* Toggle the selected state of the user */
User.prototype.selectToggle = function() {
	if (this.selected)
		this.unselect();
	else
		this.select();
}

registerLoadFunction(function(){Users.create()});
