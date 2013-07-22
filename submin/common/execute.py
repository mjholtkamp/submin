"""This module is purely to support python 2.6. If this minium is dropped
and python 2.7 is the new minimum, this file can be dropped (but code needs
to be changed a little bit of course)"""

import subprocess

def check_output(*args, **kwargs):
	"""Because python 2.6 doesn't have this, create our own version"""
	p = subprocess.Popen(*args, stdout=subprocess.PIPE, **kwargs)
	(out, err) = p.communicate()
	return out
