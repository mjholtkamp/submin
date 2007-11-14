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

function Log(message) {
	if (message == "") {
		return;
	}
	log = $c('div', {className: 'log', id: 'log', innerHTML: message, style: {top: "10px", height: "100px"}})
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
