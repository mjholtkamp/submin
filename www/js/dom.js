load('array');
var domLoaded = true;

function $(element) {
	// If there are multiple arguments return an array of elements.
	var elements = [];
	if (arguments.length > 1) {
		for (var i = 0; i < arguments.length; i++)
			elements.push($(arguments[i]));
		return elements;
	}

	if (typeof element == 'string')
		element = document.getElementById(element);
	// TODO: do we want to extend element?
	return element;
}

/* Returns a list of elements with className = class and tagName = tag */
function $$(elem, tag, classname) {
	elem = $(elem);
	var elements = elem.getElementsByTagName(tag);
	var classElements = [];
	for (var i=0; i < elements.length; i++) {
		if (elements[i].className.toLowerCase().split(/\s+/).member(classname.toLowerCase()))
			classElements[classElements.length] = elements[i];
	}
	
	return classElements;
}

/* Returns the first child of elem with tagName = tag */
function byTag(elem, tag) {
	elem = $(elem);
	for (var i = 0; i < elem.childNodes.length; i++)
		if (elem.childNodes[i].tagName == tag.toUpperCase())
			return elem.childNodes[i];
	return false;
}

/* Adds a className to element */
function addClassName(element, nClassName) {
	try {
		var classnames = element.className.split(/\s+/);
	} catch (e) {
		var classnames = new Array();
	}
	if (!classnames.member(nClassName))
		classnames[classnames.length] = nClassName;
	element.className = classnames.join(' ');
}

/* Removes a classname from element */
function removeClassName(element, oClassName) {
	if (!element.className)
		return;

	if (element.className == oClassName) {
		element.className = '';
		return;
	}

	if (element.className.indexOf(' ') < 0)
		return;

	var classnames = element.className.split(/\s+/);
	classnames.del(oClassName);
	element.className = classnames.join(' ');
}

// $c takes the name of the element and a list of properties.
// if a property is an object itself it should add all the members of that 
// object to the property (i.e. style.display)
function $c(elemName, properties) {
	var elem = document.createElement(elemName);
	if (typeof properties == 'undefined' || !properties)
		return elem;
	
	for (var property in properties) {
		if (typeof properties[property] == typeof {}) {
			for (var member in properties[property]) {
				elem[property][member] = properties[property][member];
			}
		} else {
			var setProperty = property;
			if (setProperty == 'forid')
				setProperty = 'htmlFor';
			elem[setProperty] = properties[property];
		}
	}
	
	return elem;
}

var Element = {
	show: function(elem) {
		elem = $(elem);
		elem.style.display = '';
	},
	hide: function(elem) {
		elem = $(elem);
		elem.style.display = 'none';
	}
}

