/* So how does this work?
 *
 * In the html-code you need to have 3 classes:
 *  - 'prefix'-trigger      (onclick target)
 *  - 'prefix'-icon         (the image that shows the state)
 *  - 'prefix'-object       (the node that is shown or hidden)
 *
 * The 'prefix' depends on the prefix you use, so you can have multiple
 * types of collapsables with different callbacks.
 *
 * Callbacks are called when the trigger is triggered. There are two callbacks:
 * one for collapsing and one for expanding.
 */
var collapsables_arrow_collapsed = new Image();
var collapsables_arrow_halfway = new Image();
var collapsables_arrow_expanded = new Image();

function setupCollapsables(docroot, prefix, collapseFun, expandFun) {
	var collapsables = collapsables_findClassNames(docroot, prefix + '-trigger');

	collapsables_arrow_collapsed.src = media_url + '/img/arrow-collapsed.png';
	collapsables_arrow_halfway.src = media_url + '/img/arrow-halfway.png';
	collapsables_arrow_expanded.src = media_url + '/img/arrow-expanded.png';

	var collapsables_length = collapsables.length;
	for (var idx = 0; idx < collapsables_length; ++idx) {
		var collapsable = collapsables[idx];
		var image = collapsables_getImage(prefix, collapsable);

		// if no image, assume not collapsable (sometimes needed for bootstrap)
		if (image && image.src) {
			if (image.src == collapsables_arrow_expanded.src) {
				collapsable.onclick =
					function() { arrowCollapse(prefix, this, collapseFun, expandFun); }
				collapsables_collapse(prefix, collapsable, false);
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

function collapsables_findClassNames(node, classname)
{
	var classNodes = [];
	var childNodes = node.childNodes;
	var childNodes_length = childNodes.length;
	for (var idx = 0; idx < childNodes_length; ++idx) {
		var childNode = childNodes[idx];
		if (childNode.className == classname)
			classNodes.push(childNode);

		var nodes = collapsables_findClassNames(childNode, classname);
		classNodes = classNodes.concat(nodes);
	}

	return classNodes;
}

function collapsables_findFirstClassName(node, classname)
{
	var childNodes = node.childNodes;
	var childNodes_length = childNodes.length;
	for (var idx = 0; idx < childNodes_length; ++idx) {
		if (childNodes[idx].className == classname)
			return childNodes[idx];
	}

	for (var idx = 0; idx < childNodes_length; ++idx) {
		var firstNode = collapsables_findFirstClassName(childNodes[idx],
				classname);
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
	return collapsables_findFirstClassName(root, prefix + '-trigger');
}

function collapsables_getCollapsee(prefix, node)
{
	var root = collapsables_getRoot(prefix, node);
	return collapsables_findFirstClassName(root, prefix + '-object');
}

function collapsables_getImage(prefix, node)
{
	var root = collapsables_getRoot(prefix, node);
	return collapsables_findFirstClassName(root, prefix + '-icon');
}

function collapsables_isCollapsed(prefix, node)
{
	var image = collapsables_getImage(prefix, node);
	if (image && image.src && image.src == collapsables_arrow_collapsed.src)
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
	image.src = collapsables_arrow_halfway.src;
	if (collapse) {
		setTimeout(
			function() { image.src = collapsables_arrow_collapsed.src; }, 100);
	} else {
		setTimeout(
			function() { image.src = collapsables_arrow_expanded.src; }, 100);
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
		collapsee.style.display = '';
	}

	// force refresh on certain browsers
	var root = collapsables_getRoot(prefix, triggered);
	root.style.display = 'none';
	root.style.display = '';
}

