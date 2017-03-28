function MyAjax() {
	this.serverdata = this.erromsg = this.timeout = this.stop = this.xmlhttp = !1, this.transit = !0
}
MyAjax.prototype.handle = function(a, b) {
	if(4 == a.readyState) {
		if(this.stop === !0) return;
		if(this.transit = !0, b.timeout && b.async && (clearTimeout(this.timeout), this.timeout = !1), 200 == a.status) {
			var c = this.serverdata = a.responseText.replace(/(^\s*)|(\s*$)/g, "");
			"function" == typeof b.success && b.success(c)
		} else this.erromsg = a.status, "function" == typeof b.error && b.error(a.status)
	} else if(0 == a.readyState) {
		if(this.stop === !0) return;
		b.timeout && b.async && (clearTimeout(this.timeout), this.timeout = !1), this.erromsg = a.readyState, this.transit = !0, "function" == typeof b.error && b.error(a.readyState)
	}
}, MyAjax.prototype.out = function(a) {
	this.transit = !0, this.erromsg = 504, this.stop = !0, "function" == typeof a.error && a.error(504)
}, MyAjax.prototype.carry = function(a) {
	var b, c, d, e;
	if(a.lock && !this.transit) return !1;
	this.transit = !1, this.stop = this.erromsg = !1, b = window.XMLHttpRequest ? new XMLHttpRequest : new ActiveXObject("Microsoft.XMLHTTP"), a.type = a.type.toUpperCase(), c = function() {}, "string" == typeof a.data ? (a.data = a.data.replace(/(^\s*)|(\s*$)/g, ""), c = function() {
		b.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
	}) : "[object FormData]" !== Object.prototype.toString.call(a.data) ? (a.data = "", c = function() {
		b.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
	}) : ("function" == typeof a.progress && b.upload.addEventListener("progress", a.progress, !1), a.type = "POST"), d = "" == a.data ? [null, ""] : [a.data, "?" + a.data], e = this, "function" == typeof a.complete && a.complete(), a.timeout && a.async && (this.timeout = setTimeout(function() {
		e.out(a)
	}, a.timeout)), a.async === !0 && (b.onreadystatechange = function() {
		e.handle(b, a)
	});
	try {
		switch(a.type) {
			case "POST":
				b.open("POST", a.url, a.async), c();
				break;
			default:
				b.open("GET", a.url + d[1], a.async), a.cache === !0 || b.setRequestHeader("If-Modified-Since", "0")
		}
	} catch(f) {
		return this.erromsg = 505, a.timeout && a.async && (clearTimeout(this.timeout), this.timeout = !1), this.transit = !0, "function" == typeof a.error && a.error(505), void 0
	}
	b.send(d[0]), a.async === !1 && e.handle(b, a)
};