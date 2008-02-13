load('dom');
load('window');

function Overlay() {
	var overlay = document.getElementById('overlay');
	var content;

	if (!overlay) {
		overlay = $c('div', {id: 'overlay', innerHTML: '&nbsp;'});
		document.body.appendChild(overlay);

		content = $c('div', {id: 'permissions-view'});
		document.body.appendChild(content);

		h3 = $c('h3');
		content.appendChild(h3);

		ul = $c('ul', {id: 'permissions-list'});
		content.appendChild(ul);
	}

	var windowWidth = WindowWidth();
	var windowHeight = WindowHeight();
	overlay.style.top = "0px";
	overlay.style.left = "0px";
	overlay.style.width = "" + windowWidth + "px";
	overlay.style.height = "" + windowHeight + "px";

	value = 6;
	overlay.style.opacity = value/10;
	overlay.style.filter = 'alpha(opacity=' + value*10 + ')';
	overlay.style.background = 'black';

	overlay.onclick = RemoveOverlay;

	// now position the content
	content.style.position = 'fixed';
	content.style.top = '100px';
	content.style.left = '100px';
	content.style.width = '400px';
	content.style.background = 'white';
	content.style.filter = '';

	//content.onclick = RemoveOverlay;
}

function RemoveOverlay() {
	var overlay = document.getElementById('overlay');
	var content = document.getElementById('permissions-view');

	if (overlay)
		document.body.removeChild(overlay);
	if (content)
		document.body.removeChild(content);
}

/* from quirksmode.org */
/*function WindowWidth() {
	if (self.innerWidth) {
		frameWidth = self.innerWidth;
	}
	else if (document.documentElement && document.documentElement.clientWidth) {
		frameWidth = document.documentElement.clientWidth;
	}
	else if (document.body) {
		frameWidth = document.body.clientWidth;
	}
	else return;

	return frameWidth;
}

function WindowHeight() {
	if (self.innerHeight) {
		frameHeight = self.innerHeight;
	}
	else if (document.documentElement && document.documentElement.clientHeight) {
		frameHeight = document.documentElement.clientHeight;
	}
	else if (document.body) {
		frameHeight = document.body.clientHeight;
	}
	else return;

	return frameHeight;
}
*/
