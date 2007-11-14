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
