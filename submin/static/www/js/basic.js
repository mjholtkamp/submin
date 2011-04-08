var basicLoaded = true;

var loadfunctions = [];
function registerLoadFunction(func) {
	loadfunctions[loadfunctions.length] = func;
}

function init() {
	for (var i=0; i<loadfunctions.length; i++)
		loadfunctions[i]();
}