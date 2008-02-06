
var sidebar_arrow_collapsed = new Image();
var sidebar_arrow_halfway = new Image();
var sidebar_arrow_expanded = new Image();

function setupCollapsables(docroot, prefix, collapseFun, expandFun) {
	var collapsables = showhide_findClassNames(docroot, prefix + '-trigger');

	sidebar_arrow_collapsed.src = media_url + '/img/arrow-collapsed.png';
	sidebar_arrow_halfway.src = media_url + '/img/arrow-halfway.png';
	sidebar_arrow_expanded.src = media_url + '/img/arrow-expanded.png';

	for (var idx = 0; idx < collapsables.length; ++idx) {
		collapsables[idx].onclick =
			function() { arrowCollapse(prefix, this, collapseFun, expandFun); }

		// prevent selecting trigger (looks ugly)
		collapsables[idx].onmousedown = function() { return false; }
		collapsables[idx].onselectstart = function() { return false; } // ie
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

function showhide_getRoot(prefix, node)
{
	while (node.className != prefix)
		node = node.parentNode;

	return node;
}

function showhide_getTriggers(prefix, node)
{
	var root = showhide_getRoot(prefix, node);
	return showhide_findClassNames(root, prefix + '-trigger');
}

function showhide_getCollapsees(prefix, node)
{
	var root = showhide_getRoot(prefix, node);
	return showhide_findClassNames(root, prefix + '-object');
}

function showhide_getImages(prefix, node)
{
	var root = showhide_getRoot(prefix, node);
	return showhide_findClassNames(root, prefix + '-icon');
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
	var images = showhide_getImages(prefix, triggered);
	for (var idx = 0; idx < 1; ++idx) {
		var image = images[idx];
		image.src = sidebar_arrow_halfway.src;
		if (collapse) {
			setTimeout(
				function() { image.src = sidebar_arrow_collapsed.src; }, 100);
		} else {
			setTimeout(
				function() { image.src = sidebar_arrow_expanded.src; }, 100);
		}
	}

	// do the collapse
	var collapsees = showhide_getCollapsees(prefix, triggered);
	for (var idx = 0; idx < 1; ++idx) {
		if (collapse) {
			collapsees[idx].style.display = 'none';
		} else {
			collapsees[idx].style.display = '';
		}
		root = showhide_getRoot(prefix, triggered);
		root.style.display = 'none';
		root.style.display = '';
	}

	// make sure we can expand after this
	var triggers = showhide_getTriggers(prefix, triggered);
	for (var idx = 0; idx < 1; ++idx) {
		if (collapse) {
			if (collapseFun)
				collapseFun(triggers[idx]);

			triggers[idx].onclick = function() { arrowExpand(prefix, this, collapseFun, expandFun); }
		} else {
			if (expandFun)
				expandFun(triggers[idx]);

			triggers[idx].onclick = function() { arrowCollapse(prefix, this, collapseFun, expandFun); }
		}
	}
}

