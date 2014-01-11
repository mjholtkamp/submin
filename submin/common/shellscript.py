import os
import errno

def rewriteWithSignature(filename, signature, new_hook, enable, mode=None):
	line_altered = False

	f = open(str(filename), 'a+')
	f.seek(0, 2) # seek to end of file, not all systems do this

	if f.tell() != 0:
		f.seek(0)
		alter_line = False
		new_file_content = []
		for line in f.readlines():
			if alter_line:
				if enable:
					new_file_content.append(new_hook)
				alter_line = False
				line_altered = True
				continue # filter out command

			if line == signature:
				alter_line = True
				if not enable:
					continue # filter out signature

			new_file_content.append(line)

		f.truncate(0)
		f.writelines(new_file_content)
	else:
		if enable:
			f.write("#!/bin/sh\n")

	if not line_altered and enable:
		f.write(signature)
		f.write(new_hook)
	f.close()

	if mode:
		os.chmod(str(filename), mode)

def hasSignature(filename, signature):
	try:
		f = open(filename, 'r')
	except IOError, e:
		if e.errno == errno.ENOENT:
			return False
		raise

	return signature in f.readlines()
