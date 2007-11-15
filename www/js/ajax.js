function AjaxGetRequest(url) {
	transport = new XMLHttpRequest();
	transport.open('get', url, false);
	transport.send(null);
	return transport.responseText;
}

function AjaxPostRequest(url, body) {
	transport = new XMLHttpRequest();
	transport.open('post', url, false);
	transport.send(body);
	return transport.responseText;
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

var Log_timeout;

function Log(message) {
	if (message == "") {
		return;
	}

	// first remove previous logs
	log = document.getElementById('log')
	if (log != null) {
		clearTimeout(Log_timeout)
		document.body.removeChild(log)
	}

	log = $c('div', {className: 'log', id: 'log', innerHTML: message})

	document.body.appendChild(log)
	_top = getStyle('log', 'top')
	log.style.top = _top
	height = getStyle('log', 'height')
	log.style.height = height

	value = 5;
	log.style.opacity = value/10;
	log.style.filter = 'alpha(opacity=' + value*10 + ')';

	Log_timeout = setTimeout("RemoveLog()", 2000)
}

function RemoveLog() {
	log = document.getElementById('log')
	_top = parseInt(log.style.top)
	height = parseInt(log.style.height)
	if (_top + height > 0) {
		log.style.top = "" + (_top - 5) + "px";
		Log_timeout = setTimeout("RemoveLog()", 10)
	} else {
		document.body.removeChild(log)
	}
}
