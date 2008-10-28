load('log.js')

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

function Response(transport) {
	var doc = transport.responseXML;
	// DEBUG
	if (submin.debug) {
		var string = (new XMLSerializer()).serializeToString(doc);
		alert(string);
	}
	var commands_xml = doc.getElementsByTagName('command');
	var commands = [];
	for (var i = 0; i < commands_xml.length; ++i) {
		commands.push(newResponseCommand(commands_xml[i]));
	}
	return commands;
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
	if (submin.debug)
		alert(url + "?ajax&" + params);
	var transport = new XMLHttpRequest();
	transport.open('post', url, true);
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

function AjaxAsyncPostLog(url, params) {
	AjaxAsyncPostRequest(url, params, LogResponse);
}

