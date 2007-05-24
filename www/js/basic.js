var basicLoaded = true;

var loaded = [];
function load(scriptName) {
	if (scriptName.indexOf('.js') == -1)
		scriptName += '.js';

	for (var i=0; i<loaded.length;i++) {
		if (loaded[i] == scriptName)
			return;
	}

	// TODO: rewrite to use multiple arguments.
	var scripttags = document.getElementsByTagName('script');
	for (var i=0; i<scripttags.length; i++) {
		var script = scripttags[i];
		if (script.src.indexOf('basic.js') >= 0) {
			// We have the basic.js, now try and find the path
			var path = script.src.replace(/basic\.js$/, '');
			addScript(path + scriptName);
			loaded.push(scriptName);
		}
	}
}

function addScript(path) {
	document.write('<script type="text/javascript" src="' + path + '"></script>');
}

var loadfunctions = [];
function registerLoadFunction(func) {
	loadfunctions[loadfunctions.length] = func;
}

function init() {
	for (var i=0; i<loadfunctions.length; i++)
		loadfunctions[i]();
}