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
function getStyle( element, cssRule )
{
	if (document.defaultView && document.defaultView.getComputedStyle) {
		var value = document.defaultView.getComputedStyle(element, '').getPropertyValue(
			cssRule.replace( /[A-Z]/g, function(match, char) {
				return "-" + char.toLowerCase();
			} )
		);
	}
	else if (element.currentStyle) var value = element.currentStyle[cssRule];
	else                           var value = false;
	return value;
}

function Log(message) {
	if (message == "") {
		return;
	}
	log = $c('div', {className: 'log', id: 'log', innerHTML: message})

	top = getStyle(log, 'top')
	log.style.top = top
	height = getStyle(log, 'height')
	log.style.height = height
	document.body.appendChild(log)
	setTimeout("RemoveLog()", 2000)
}

function RemoveLog() {
	log = document.getElementById('log')
	top = parseInt(log.style.top)
	height = parseInt(log.style.height)
	if (top + height > 0) {
		log.style.top = "" + (top - 5) + "px";
		setTimeout("RemoveLog()", 10)
	} else {
		document.body.removeChild(log)
	}
}
