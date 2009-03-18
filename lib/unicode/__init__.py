# -*- coding: utf-8 -*-
"""Tools to convert from and to unicode"""

import re

def uc_str(obj, encoding='utf-8', errors='replace'):
	if isinstance(obj, str):
		return unicode(obj, encoding, errors)
	if isinstance(obj, unicode):
		return obj

	return unicode(str(obj), encoding, errors)

def _url_uc_to_uc_callback(matchobj):
	s = matchobj.group(0)
	u = s.replace("%", "\\")
	return unicode(u, 'unicode_escape')

def url_uc_decode(s):
	"""Convert expressions like '%uFFFF' to '\\uFFFF' and encode as unicode.
	This way of encoding unicode in urls is often used by javascript."""
	return re.sub('%u[a-zA-Z0-9]{4,4}', _url_uc_to_uc_callback, s)