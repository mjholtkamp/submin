function Response(transport) {
	doc = transport.responseXML;
	response = {};
	// DEBUG
	//var string = (new XMLSerializer()).serializeToString(doc);
	//alert(string);
	success = doc.getElementsByTagName('success')[0].childNodes[0].nodeValue;
	var text = doc.getElementsByTagName('text');
	if (text)
		text = text[0];
	if (text)
		text = text.childNodes[0];
	if (text)
		text = text.nodeValue;
	if (!text)
		text = '';
	response['text'] = text;
	response['xml'] = doc;

	if (success.toLowerCase() == 'true') {
		response['success'] = true
	} else {
		response['success'] = false
	}
	return response
}

function AjaxSyncGetRequest(url, params) {
	transport = new XMLHttpRequest();
	transport.open('get', url + '?ajax&' + params, false);
	transport.send(null);
	return Response(transport)
}

function AjaxSyncPostRequest(url, params) {
	transport = new XMLHttpRequest();
	transport.open('post', url, false);
	transport.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	transport.setRequestHeader("Connection", "close");
	transport.send('ajax&' + params);
	return Response(transport)
}

function AjaxSyncPostLog(url, params) {
	var response = AjaxSyncPostRequest(url, params)
	Log(response.text, response.success)
	return response.success
}

function AjaxAsyncPostRequest(url, params, callback) {
	transport = new XMLHttpRequest();
	transport.open('post', url, false);
	transport.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	transport.setRequestHeader("Connection", "close");
	transport.onreadystatechange = function() {
		AjaxCallback(transport, callback);
	};
	transport.send('ajax&' + params);

}

function AjaxCallback(transport, callback) {
	if (transport.readyState == 4) {
		var response = Response(transport);
		callback(response);
	}
}

function AjaxLog(response) {
	Log(response.text, response.success);
}

function AjaxAsyncPostLog(url, params) {
	AjaxAsyncPostRequest(url, params, AjaxLog);
}

