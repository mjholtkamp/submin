/* Constructor. Options is a dictionary.
 * Expected options:
 * - selectorId: The id of the ul to add f.i. every group and the
 *   	dropdown with all the remaining groups to.
 * - urlPrefix: The name of the current item is added to this prefix to link
 *   	to f.i. a group
 * - init: callback-function which returns two lists in a dictionary:
 *   	added and addable. The first being the list with the items which are
 *   	already part of the Selector, and addable items which can be added.
 *   	This method is also called when re-initializing after a change.
 * - addCallback: callback-function, expecting the name of the item to be
 *   	added. This usually does an Ajax-request to add f.i. a user to a group.
 * - removeCallback: Analogous to addCallback, only for removing. Also expects
 *   	the name of the item to be removed.
 * - canLink: is a user allowed to see a link to the other object? This is a
 *   	function, expecting the name of the current object.
 */
function Selector(options) {
	this.options = options;
	this.list = document.getElementById(this.options.selectorId);
	this.init();
}

/* Creates the add/remove button for each item */
Selector.prototype.makeButton = function(className) {
	var link = $c("a", {"href": "#", "className": className});
	var imgSrc = base_url + "/img/" +
		(className == "remover" ? "min.gif" : "plus.gif");
	var img = $c("img", {"src": imgSrc, "className": className});
	link.appendChild(img);
	return link;
}

/* Reinitializes the list after a change. */
Selector.prototype.reInit = function() {
	// Make the list empty before calling init().
	for (var item_idx=this.list.childNodes.length; item_idx--;)
		this.list.removeChild(this.list.childNodes[item_idx]);
	this.init();
}

Selector.prototype.init = function() {
	var callbackValue = this.options.init();

	// The li-items
	var added = callbackValue["added"];
	for (var added_idx=0; added_idx < added.length; ++added_idx)
		this.setupAddedItem(added[added_idx]);

	// The dropdown

	// Don't show it to non-admins!
	if (!is_admin)
		return;

	var addable = callbackValue["addable"];
	this.setupSelect();
	for (var addable_idx=0; addable_idx < addable.length; ++addable_idx)
		this.addOption(addable[addable_idx]);
	if (!addable.length)
		this.disableSelect();
}

Selector.prototype.setupAddedItem = function(added) {
		var item = $c("li");
		item.name = added;
		if (!this.options.canLink(added))
			item.appendChild(document.createTextNode(added));
		else
		{
			var link = $c("a", {"href": this.options.urlPrefix + added});
			link.appendChild(document.createTextNode(added));
			item.appendChild(link);
		}

		if (is_admin)
		{
			var remover = this.makeButton("remover");
			item.appendChild(remover);

			var _this = this; // this is out of scope in onclick below!
			remover.onclick = function() {
				_this.options.removeCallback(this.parentNode.name);
				_this.reInit();
				return false;
			};
		}

		this.list.appendChild(item);
}

Selector.prototype.disableSelect = function() {
	this.select.disabled = true;

	// Disable the add-button and change the cursor-style. Maybe hide?
	this.select.adder.disabled_onclick = this.select.adder.onclick;
	this.select.adder.firstChild.src = base_url + "/img/plus-greyed.png";
	this.select.adder.onclick = function() { return false; }
	this.select.adder.style.cursor = 'default';
}

Selector.prototype.setupSelect = function() {
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

		_this.options.addCallback(groupname);
		_this.reInit();
		return false;
	}
	item.appendChild(adder);
	this.list.appendChild(item);
	this.addOption("---");
}

Selector.prototype.addOption = function(name) {
	var option = $c("option");
	option.appendChild(document.createTextNode(name));
	this.select.appendChild(option);
}
