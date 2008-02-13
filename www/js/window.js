/* from quirksmode.org */
function WindowWidth() {
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

