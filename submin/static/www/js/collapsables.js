/* So how does this work?
 *
 * In the html-code you need to have 3 classes:
 *  - 'prefix' c_trigger      (onclick target)
 *  - 'prefix' c_icon         (the image that shows the state)
 *  - 'prefix' c_object       (the node that is shown or hidden)
 *
 * The 'prefix' depends on the prefix you use, so you can have multiple
 * types of collapsables with different callbacks.
 *
 * Callbacks are called when the trigger is triggered. There are two callbacks:
 * one for collapsing and one for expanding.
 */

function setupCollapsables(docroot, prefix, collapseFun, expandFun) {
	var collapsables = collapsables_findClassNames(docroot, prefix, 'c_trigger');

	var collapsables_length = collapsables.length;
	for (var idx = 0; idx < collapsables_length; ++idx) {
		var collapsable = collapsables[idx];
		var image = collapsables_getImage(prefix, collapsable);

		// if no image, assume not collapsable (sometimes needed for bootstrap)
		if (image) {
			// Set the overflow to 'hidden', this is a workaround to make
			// sure the elements are rerendered everytime it is hidden/shown.
			// This is needed for example in Opera.
			var root = collapsables_getCollapsee(prefix, image);
			root.style.overflow = 'hidden';

			if (hasClassName(image, 'expanded')) {
				collapsable.onclick =
					function() { arrowCollapse(prefix, this, collapseFun, expandFun); }
				collapsables_collapse(prefix, collapsable, false);
				var trigger = collapsables_getTrigger(prefix, collapsable);
				expandFun(trigger);
			} else {
				collapsable.onclick =
					function() { arrowExpand(prefix, this, collapseFun, expandFun); }
				collapsables_collapse(prefix, collapsable, true);
			}

			// prevent selecting trigger (looks ugly)
			collapsable.onmousedown = function() { return false; }
			collapsable.onselectstart = function() { return false; } // ie
		}
	}
}

function collapsables_findClassNames(node, prefix, classname)
{
	var classNodes = [];
	var current = node;
	for (;;) {
		if (hasClassName(current, prefix) && hasClassName(current, classname))
			classNodes.push(current);

		if (current.firstChild) {
			current = current.firstChild;
			continue;
		}

		if (current.nextSibling) {
			current = current.nextSibling;
			continue;
		}

		do {
			current = current.parentNode;
			if (current == node || !current)
				return classNodes;
		} while (!current.nextSibling);
		current = current.nextSibling;
	}
}

function collapsables_findFirstClassName(node, prefix, classname)
{
	var childNodes = node.childNodes;
	var childNodes_length = childNodes.length;
	for (var idx = 0; idx < childNodes_length; ++idx) {
		if (hasClassName(childNodes[idx], prefix) && hasClassName(childNodes[idx], classname))
			return childNodes[idx];
	}

	for (var idx = 0; idx < childNodes_length; ++idx) {
		var firstNode = collapsables_findFirstClassName(childNodes[idx],
				prefix, classname);
		if (firstNode)
			return firstNode;
	}

	return null;
}

function collapsables_getRoot(prefix, node)
{
	while (node.className != prefix)
		node = node.parentNode;

	return node;
}

function collapsables_getTrigger(prefix, node)
{
	var root = collapsables_getRoot(prefix, node);
	return collapsables_findFirstClassName(root, prefix, 'c_trigger');
}

function collapsables_getCollapsee(prefix, node)
{
	var root = collapsables_getRoot(prefix, node);
	return collapsables_findFirstClassName(root, prefix, 'c_object');
}

function collapsables_getImage(prefix, node)
{
	var root = collapsables_getRoot(prefix, node);
	return collapsables_findFirstClassName(root, prefix, 'c_icon');
}

function collapsables_isCollapsed(prefix, node)
{
	var image = collapsables_getImage(prefix, node);
	if (image && hasClassName(image, 'collapsed'))
		return true;

	return false;
}

function arrowCollapse(prefix, triggered, collapseFun, expandFun)
{
	arrowChange(prefix, triggered, true, collapseFun, expandFun);
}

function arrowExpand(prefix, triggered, collapseFun, expandFun)
{
	arrowChange(prefix, triggered, false, collapseFun, expandFun);
}

function arrowChange(prefix, triggered, collapse, collapseFun, expandFun)
{
	// animate image
	var image = collapsables_getImage(prefix, triggered);
	if (collapse) {
		removeClassName(image, 'expanded');
	} else {
		removeClassName(image, 'collapsed');
	}
	addClassName(image, 'halfway');
	if (collapse) {
		setTimeout(
			function() { addClassName(image, 'collapsed'); removeClassName(image, 'halfway'); }, 100);
	} else {
		setTimeout(
			function() { addClassName(image, 'expanded'); removeClassName(image, 'halfway'); }, 100);
	}
	collapsables_collapse(prefix, triggered, collapse);

	// triggered isn't necessarily the trigger itself, can be a
	// childnode, so get the real trigger node
	var trigger = collapsables_getTrigger(prefix, triggered);
	if (collapse) {
		if (collapseFun)
			collapseFun(trigger);

		trigger.onclick =
			function() { arrowExpand(prefix, this, collapseFun, expandFun); }
	} else {
		if (expandFun)
			expandFun(trigger);

		trigger.onclick =
			function() { arrowCollapse(prefix, this, collapseFun, expandFun); }
	}
}

function collapsables_collapse(prefix, triggered, collapse)
{
	// do the collapse
	var collapsee = collapsables_getCollapsee(prefix, triggered);
	if (collapse) {
		collapsee.style.display = 'none';
	} else {
		collapsee.style.display = 'block';
	}
	// force refresh on certain browsers This is needed for the repositories
	// edit box (Safari, ff, ??)
	var root = collapsables_getRoot(prefix, triggered);
	root.style.display = 'none';
	root.style.display = 'block';
}

