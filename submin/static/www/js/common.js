/* ==== Array functions ==== */
if (typeof Array.prototype.member == 'undefined') {
	Array.prototype.member = function(element) {
		for (var i=0; i<this.length; i++) {
			if (this[i] == element)
				return true;
		}
		return false;
	}
}

if (typeof Array.prototype.index == 'undefined') {
	Array.prototype.index = function(element) {
		for (var i=0; i < this.length; i++) {
			if (this[i] == element)
				return i;
		}
		return -1;
	}
}

if (typeof Array.prototype.del == 'undefined') {
	Array.prototype.del = function(element) {
		this.splice(this.index(element), 1)
	}
}

if (typeof Array.prototype.push == 'undefined') {
	Array.prototype.push = function()  {
		for (var i = 0; i < arguments.length; i++) {
			this[this.length] = arguments[i];
		}
		return this.length;
	}
}

// This idea is from prototype (prototype.conio.net)
var $break    = new Object();
var $continue = new Object();

if (typeof Array.prototype.each == 'undefined') {
	Array.prototype.each = function (func) {
		try {
			for (var i=0; i<this.length; i++) {
				try {
					func(this[i], i);
				} catch (e) {
					if (e != $continue)
						throw e;
				}
			}
		} catch (e) {
			if (e != $break)
				throw e;
		}
	}
}

if (typeof Array.prototype.iter == 'undefined') {
	Array.prototype.iter = function() {
		this.iteration = 0;
		return this.current();
	}
	Array.prototype.hasNext = function() {
		return this.iteration < this.length;
	}
	Array.prototype.next = function() {
		this.iteration++;
		return this.current();
	}
	Array.prototype.current = function() {
		if (this.iteration == this.length)
			return null;
		return this[this.iteration];
	}
}

/* ==== DOM functions ==== */
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

function hasClassName(element, oClassName) {
	if (!element.className)
		return false;

	if (element.className == oClassName)
		return true;

	if (element.className.indexOf(' ') < 0)
		return false;

	var classnames = element.className.split(/\s+/);
	return -1 != classnames.indexOf(oClassName);
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

/* ==== Resizing helper functions ==== */

/* from quirksmode.org */
function WindowWidth() {
	if (self.innerWidth) {
		frameWidth = self.innerWidth;
	}
	else if (document.documentElement && document.documentElement.clientWidth) {
		frameWidth = document.documentElement.clientWidth;
	}
	else if (document.body) {
		frameWidth = document.body.clientWidth;
	}
	else return;

	return frameWidth;
}

function WindowHeight() {
	if (self.innerHeight) {
		frameHeight = self.innerHeight;
	}
	else if (document.documentElement && document.documentElement.clientHeight) {
		frameHeight = document.documentElement.clientHeight;
	}
	else if (document.body) {
		frameHeight = document.body.clientHeight;
	}
	else return;

	return frameHeight;
}

/* ==== LOG Functions ==== */
var Log_timeout;

function Log(message, success) {
	if (message == "")
		return;

	if (!document.body)
		return;

	// first remove previous logs
	RemoveLog()

	var classname = 'log_message';
	if (!success)
		classname = 'log_error';

	message = message.replace(/ /g, '&nbsp;');
	message = message.replace(/\n/g, '<br />\n');
	log = $c('div', {className: classname, id: 'log', innerHTML: message})

	document.body.appendChild(log)
	_top = getStyle('log', 'top')
	log.style.top = _top
	width = parseInt(getStyle('log', 'width'));
	windowWidth = WindowWidth();
	log.style.left = "" + (windowWidth/2 - width/2) + "px";

	value = 9;
	log.style.opacity = value/10;
	log.style.filter = 'alpha(opacity=' + value*10 + ')';

	// remove on click
	log.onclick = RemoveLog

	if (success)
		Log_timeout = setTimeout("FadeLog(" + value + ")", 2000)
	else
		log.innerHTML += "<br /><small>Click to close</small>";
}

function RemoveLog() {
	log = document.getElementById('log')
	if (log != null) {
		clearTimeout(Log_timeout)
		document.body.removeChild(log)
	}
}

function FadeLog(value) {
	log = document.getElementById('log')
	value--;
	if (value > 0) {
		log.style.opacity = value/10;
		log.style.filter = 'alpha(opacity=' + value*10 + ')';
		Log_timeout = setTimeout("FadeLog(" + value + ")", 50)
	} else {
		RemoveLog(log)
	}
}

// from: http://www.elektronaut.no/articles/2006/06/07/computed-styles
// Get the computed css property
function getStyle(element, cssRule)
{
	if (typeof element == 'string')
		element = document.getElementById(element)

	if (document.defaultView && document.defaultView.getComputedStyle) {
		// don't call replace with a function, won't work in safari
		prop = cssRule.replace(/([A-Z])/g, "-$1");
		prop = prop.toLowerCase();
		var style = document.defaultView.getComputedStyle(element, '');
		// style will be null if element isn't visible (not added to
		// document)
		if (style == null)
			return

		var value = style.getPropertyValue(prop);
	}
	else if (element.currentStyle) var value = element.currentStyle[cssRule];
	else                           var value = false;
	return value;
}


/* ==== Sorting functions ==== */

function humanCmp(a, b) {
	aa = a.split(/(\d+)/);
	bb = b.split(/(\d+)/);

	for(var x = 0; x < Math.max(aa.length, bb.length); x++) {
		if(aa[x] != bb[x]) {
			var cmp1 = (isNaN(parseInt(aa[x],10)))? aa[x] : parseInt(aa[x],10);
			var cmp2 = (isNaN(parseInt(bb[x],10)))? bb[x] : parseInt(bb[x],10);
			if(cmp1 == undefined || cmp2 == undefined)
				return aa.length - bb.length;
			else
				return (cmp1 < cmp2) ? -1 : 1;
		}
	}
	return 0;
}

function xmlSortByName(a, b) {
	return humanCmp(a.getAttribute("name"), b.getAttribute("name"));
}

/* ==== AJAX Functions ==== */

function Submin_config() {
	this.debug = false;
}
submin = new Submin_config();

function newResponseCommand(command_xml) {
	var command = {};
	command['name'] = command_xml.getAttribute('name');
	
	var success = command_xml.getAttribute('success');
	if (success.toLowerCase() == 'true') {
		command['success'] = true;
	} else {
		command['success'] = false;
	}

	var text = command_xml.getElementsByTagName('text');
	if (text && text.length > 0) {
		text = text[0];
	} else {
		text = null;
	}

	if (text)
		text = text.childNodes[0];
	if (text)
		text = text.nodeValue;
	if (!text)
		text = '';

	command['text'] = text;
	command['xml'] = command_xml;

	return command;
}

function FindResponse(response, name) {
	for (var i = 0; i < response.length; ++i) {
		if (response[i]['name'] == name) {
			return response[i];
		}
	}
	return null;
}

function LogResponse(response) {
	text_accum = '';
	success = true;
	for (var i = 0; i < response.length; ++i) {
		var text = response[i]['text'];
		if (text) {
			if (!response[i].success)
				success = false;
			text_accum += text;
		}
	}
	Log(text_accum, success);
}

function XMLtoResponse(doc) {
	var commands_xml = doc.getElementsByTagName('command');
	var commands = [];
	for (var i = 0; i < commands_xml.length; ++i) {
		commands.push(newResponseCommand(commands_xml[i]));
	}
	return commands;
}

function Response(transport) {
	var doc = transport.responseXML;
	if (doc == null) {
		Log("Something really bad happened: Didn't get any XML. RAW text: " + transport.responseText, false);
		return [];
	}

	// DEBUG
	if (submin.debug) {
		var string = (new XMLSerializer()).serializeToString(doc);
		alert(string);
	}
	return XMLtoResponse(doc);
}

function AjaxSyncGetRequest(url, params) {
	var transport = new XMLHttpRequest();
	transport.open('get', url + '?ajax&' + params, false);
	transport.send(null);
	return Response(transport)
}

function AjaxSyncPostRequest(url, params) {
	if (submin.debug)
		alert(url + "?ajax&" + params);
	var transport = new XMLHttpRequest();
	transport.open('post', url, false);
	transport.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	transport.send('ajax&' + params);
	return Response(transport)
}

function AjaxSyncPostLog(url, params) {
	var response = AjaxSyncPostRequest(url, params)
	Log(response.text, response.success)
	return response.success
}

function AjaxAsyncPostRequest(url, params, callback, callback_param) {
	if (submin.debug)
		alert(url + "?ajax&" + params);
	var transport = new XMLHttpRequest();
	transport.open('post', url, true);
	transport.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	transport.onreadystatechange = function() {
		AjaxCallback(transport, callback, callback_param);
	};
	transport.send('ajax&' + params);

}

function AjaxCallback(transport, callback, callback_param) {
	if (transport.readyState == 4) {
		var response = Response(transport);
		callback(response, callback_param);
	}
}

function AjaxAsyncPostLog(url, params) {
	AjaxAsyncPostRequest(url, params, LogResponse);
}

function escape_plus(string) {
	return escape(string).replace(/\+/g, "%2b");
}
