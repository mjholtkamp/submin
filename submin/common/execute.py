"""This module is purely to support python 2.6. If this minium is dropped
and python 2.7 is the new minimum, this file can be dropped (but code needs
to be changed a little bit of course)"""

import subprocess

def check_output(*args, **kwargs):
	"""Because python 2.6 doesn't have this, create our own version"""
	try:
		return subprocess.check_output(*args, **kwargs)
	except AttributeError:
		pass

	p = subprocess.Popen(*args, stdout=subprocess.PIPE, **kwargs)
	(out, err) = p.communicate()
	if p.returncode:
		""" python 2.6 version of subprocess does not support 3rd argument
		(output), so only returncode and cmd are given"""
		e = subprocess.CalledProcessError(p.returncode, ' '.join(*args))
		e.output = out
		raise e

	return out
