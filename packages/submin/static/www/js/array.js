if (typeof Array.prototype.member == 'undefined') {
	Array.prototype.member = function(element) {
		for (var i=0; i<this.length; i++) {
			if (this[i] == element)
				return true;
		}
		return false;
	}
}

if (typeof Array.prototype.index == 'undefined') {
	Array.prototype.index = function(element) {
		for (var i=0; i < this.length; i++) {
			if (this[i] == element)
				return i;
		}
		return -1;
	}
}

if (typeof Array.prototype.del == 'undefined') {
	Array.prototype.del = function(element) {
		this.splice(this.index(element), 1)
	}
}

if (typeof Array.prototype.push == 'undefined') {
	Array.prototype.push = function()  {
		for (var i = 0; i < arguments.length; i++) {
			this[this.length] = arguments[i];
		}
		return this.length;
	}
}

// This idea is from prototype (prototype.conio.net)
var $break    = new Object();
var $continue = new Object();

if (typeof Array.prototype.each == 'undefined') {
	Array.prototype.each = function (func) {
		try {
			for (var i=0; i<this.length; i++) {
				try {
					func(this[i], i);
				} catch (e) {
					if (e != $continue)
						throw e;
				}
			}
		} catch (e) {
			if (e != $break)
				throw e;
		}
	}
}

if (typeof Array.prototype.iter == 'undefined') {
	Array.prototype.iter = function() {
		this.iteration = 0;
		return this.current();
	}
	Array.prototype.hasNext = function() {
		return this.iteration < this.length;
	}
	Array.prototype.next = function() {
		this.iteration++;
		return this.current();
	}
	Array.prototype.current = function() {
		if (this.iteration == this.length)
			return null;
		return this[this.iteration];
	}
}