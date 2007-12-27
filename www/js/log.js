var Log_timeout;

function Log(message, success) {
	if (message == "") {
		return;
	}

	// first remove previous logs
	RemoveLog()

	var classname = 'log_message';
	if (!success)
		classname = 'log_error';

	log = $c('div', {className: classname, id: 'log', innerHTML: message})

	document.body.appendChild(log)
	_top = getStyle('log', 'top')
	log.style.top = _top
	height = getStyle('log', 'height')
	log.style.height = height
	width = parseInt(getStyle('log', 'width'))
	windowWidth = WindowWidth()
	log.style.left = "" + (windowWidth/2 - width/2) + "px";

	value = 9;
	log.style.opacity = value/10;
	log.style.filter = 'alpha(opacity=' + value*10 + ')';

	// remove on click
	log.onclick = RemoveLog

	if (success)
		Log_timeout = setTimeout("MoveLog()", 2000)
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

function MoveLog() {
	log = document.getElementById('log')
	_top = parseInt(log.style.top)
	height = parseInt(log.style.height)
	if (_top + height > 0) {
		log.style.top = "" + (_top - 5) + "px";
		Log_timeout = setTimeout("MoveLog()", 10)
	} else {
		RemoveLog(log)
	}
}

/* from quirksmode.org */
function WindowWidth() {
	if (self.innerWidth)
	{
		frameWidth = self.innerWidth;
	}
	else if (document.documentElement && document.documentElement.clientWidth)
	{
		frameWidth = document.documentElement.clientWidth;
	}
	else if (document.body)
	{
		frameWidth = document.body.clientWidth;
	}
	else return;

	return frameWidth;
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


