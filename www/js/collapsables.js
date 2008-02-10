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
var sidebar_arrow_collapsed = new Image();
var sidebar_arrow_halfway = new Image();
var sidebar_arrow_expanded = new Image();

function setupCollapsables(docroot, prefix, collapseFun, expandFun) {
	var collapsables = showhide_findClassNames(docroot, prefix + '-trigger');

	sidebar_arrow_collapsed.src = media_url + '/img/arrow-collapsed.png';
	sidebar_arrow_halfway.src = media_url + '/img/arrow-halfway.png';
	sidebar_arrow_expanded.src = media_url + '/img/arrow-expanded.png';

	for (var idx = 0; idx < collapsables.length; ++idx) {
		image = showhide_getImage(prefix, collapsables[idx]);

		// if no image, assume not collapsable (sometimes needed for bootstrap)
		if (image) {
			if (image.src == sidebar_arrow_expanded.src) {
				collapsables[idx].onclick =
					function() { arrowCollapse(prefix, this, collapseFun, expandFun); }
				showhide_collapse(prefix, collapsables[idx], false);
			} else {
				collapsables[idx].onclick =
					function() { arrowExpand(prefix, this, collapseFun, expandFun); }
				showhide_collapse(prefix, collapsables[idx], true);
			}

			// prevent selecting trigger (looks ugly)
			collapsables[idx].onmousedown = function() { return false; }
			collapsables[idx].onselectstart = function() { return false; } // ie
		}
	}
}

function showhide_findClassNames(node, classname)
{
	var classNodes = [];
	for (var idx = 0; idx < node.childNodes.length; ++idx) {
		if (node.childNodes[idx].className == classname)
			classNodes.push(node.childNodes[idx]);

		var nodes = showhide_findClassNames(node.childNodes[idx], classname);
		classNodes = classNodes.concat(nodes);
	}

	return classNodes;
}

function showhide_findFirstClassName(node, classname)
{
	classNodes = showhide_findClassNames(node, classname);
	return classNodes[0];
}

function showhide_getRoot(prefix, node)
{
	while (node.className != prefix)
		node = node.parentNode;

	return node;
}

function showhide_getTrigger(prefix, node)
{
	var root = showhide_getRoot(prefix, node);
	return showhide_findFirstClassName(root, prefix + '-trigger');
}

function showhide_getCollapsee(prefix, node)
{
	var root = showhide_getRoot(prefix, node);
	return showhide_findFirstClassName(root, prefix + '-object');
}

function showhide_getImage(prefix, node)
{
	var root = showhide_getRoot(prefix, node);
	return showhide_findFirstClassName(root, prefix + '-icon');
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
	var image = showhide_getImage(prefix, triggered);
	image.src = sidebar_arrow_halfway.src;
	if (collapse) {
		setTimeout(
			function() { image.src = sidebar_arrow_collapsed.src; }, 100);
	} else {
		setTimeout(
			function() { image.src = sidebar_arrow_expanded.src; }, 100);
	}
	showhide_collapse(prefix, triggered, collapse);

	// triggered isn't necessarily the trigger itself, can be a
	// childnode, so get the real trigger node
	var trigger = showhide_getTrigger(prefix, triggered);
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

function showhide_collapse(prefix, triggered, collapse)
{
	// do the collapse
	var collapsee = showhide_getCollapsee(prefix, triggered);
	if (collapse) {
		collapsee.style.display = 'none';
	} else {
		collapsee.style.display = '';
	}

	// force refresh on certain browsers
	root = showhide_getRoot(prefix, triggered);
	root.style.display = 'none';
	root.style.display = '';
}

