// copied from:
// http://en.design-noir.de/webdev/JS/XMLHttpRequest-IE/

if (!window.XMLHttpRequest)
	window.XMLHttpRequest = function() { return new ActiveXObject('Microsoft.XMLHTTP'); }
