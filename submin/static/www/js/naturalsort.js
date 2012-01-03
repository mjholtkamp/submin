function humanCmp(a, b) {
	aa = a.split(/(\d+)/);
	bb = b.split(/(\d+)/);

	for(var x = 0; x < Math.max(aa.length, bb.length); x++) {
		if(aa[x] != bb[x]) {
			var cmp1 = (isNaN(parseInt(aa[x],10)))? aa[x] : parseInt(aa[x],10);
			var cmp2 = (isNaN(parseInt(bb[x],10)))? bb[x] : parseInt(bb[x],10);
			if(cmp1 == undefined || cmp2 == undefined)
				return aa.length - bb.length;
			else
				return (cmp1 < cmp2) ? -1 : 1;
		}
	}
	return 0;
}
