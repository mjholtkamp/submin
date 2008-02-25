/* Constructor. Options is a dictionary.
 * Expected options:
 * - selectorId: The id of the ul to add f.i. every group and the
 *   	dropdown with all the remaining groups to.
 * - urlPrefix: The name of the current item is added to this prefix to link
 *   	to f.i. a group
 * - init: callback-function which returns two lists in a dictionary:
 *   	added and addable. The first being the list with the items which are
 *   	already part of the PermissionsEditor, and addable items which can be added.
 *   	This method is also called when re-initializing after a change.
 * - addCallback: callback-function, expecting the name of the item to be
 *   	added. This usually does an Ajax-request to add f.i. a user to a group.
 * - removeCallback: Analogous to addCallback, only for removing. Also expects
 *   	the name of the item to be removed.
 * - canLink: is a user allowed to see a link to the other object? This is a
 *   	function, expecting the name of the current object.
 */
function PermissionsEditor(options) {
	this.options = options;
	this.list = document.getElementById(this.options.editorId);
	this.init();
}

/* Creates the add/remove button for each item */
PermissionsEditor.prototype.makeButton = function(className) {
	var link = $c("a", {"href": "#", "className": className});
	var imgSrc = media_url + "/img/" +
		(className == "remover" ? "min.gif" : "plus.gif");
	var img = $c("img", {"src": imgSrc, "className": className});
	link.appendChild(img);
	return link;
}

/* Reinitializes the list after a change. */
PermissionsEditor.prototype.reInit = function() {
	// Make the list empty before calling init().
	for (var item_idx=this.list.childNodes.length; item_idx--;)
		this.list.removeChild(this.list.childNodes[item_idx]);
	this.init();
}

PermissionsEditor.prototype.init = function() {
	var callbackValue = this.options.initCallback(this.options.path);

	for (var item_idx=this.list.childNodes.length; item_idx--;)
		this.list.removeChild(this.list.childNodes[item_idx]);

	// The li-items
	var added = callbackValue["added"];
	for (var added_idx=0; added_idx < added.length; ++added_idx)
		this.setupAddedItem(added[added_idx]);

	// The dropdown
	var addable = callbackValue["addable"];
	this.setupSelect();
	for (var addable_idx=0; addable_idx < addable.length; ++addable_idx)
		this.addOption(addable[addable_idx]);
	if (!addable.length)
		this.disableSelect();
}

PermissionsEditor.prototype.setupAddedItem = function(added) {
		var item = $c("li");
		item.name = added['name'];
		var permissions = added['permissions'];
		if (permissions == '')
			permissions = 'none';

		item.appendChild($c("label", {"innerHTML": added['name']}));
		item.appendChild($c("span", {"innerHTML": permissions}));

		var remover = this.makeButton("remover");
		item.appendChild(remover);

		var _this = this; // this is out of scope in onclick below!
		remover.onclick = function() {
			var name = this.parentNode.name;
			_this.options.removeCallback(name, _this.options.path);
			_this.reInit();
			return false;
		};

		this.list.appendChild(item);
}

PermissionsEditor.prototype.disableSelect = function() {
	this.select.disabled = true;

	// Disable the add-button and change the cursor-style. Maybe hide?
	this.select.adder.disabled_onclick = this.select.adder.onclick;
	this.select.adder.onclick = function() { return false; }
	this.select.adder.style.cursor = 'default';
}

PermissionsEditor.prototype.setupSelect = function() {
	this.select = $c("select");
	var item = $c("li");
	item.appendChild(this.select);
	var adder = this.makeButton("adder");
	this.select.adder = adder;
	var _this = this; // this is out of scope in onclick below!

	adder.onclick = function() {
		var select = _this.select
		var groupname = select.options[select.selectedIndex].innerHTML;

		if (groupname == "---") {
			Log('Please select an item first', false)
			return false;
		}

		groupname = groupname.replace('[User] ', '');
		groupname = groupname.replace('[Group] ', '@');

		_this.options.addCallback(groupname, _this.options.path);
		_this.reInit();
		return false;
	}
	item.appendChild(adder);
	this.list.appendChild(item);
	this.addOption("---");
}

PermissionsEditor.prototype.addOption = function(name) {
	var option = $c("option");
	var displayname;
	if (name[0] == '@') {
		displayname = '[Group] ' + name.substring(1, name.length);
	} else {
		if (name != "---") {
			displayname = '[User] ' + name;
		} else {
			displayname = name;
		}
	}

	option.appendChild(document.createTextNode(displayname));
	this.select.appendChild(option);
}
