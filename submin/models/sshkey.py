import os
import tempfile
import subprocess

from submin.common.execute import check_output

def openssh_import(sshtype, ssh_key):
	(fd, fname) = tempfile.mkstemp(text=True)
	os.close(fd)
	file(fname, 'w').write(ssh_key)
	try:
		openssh_format = check_output(['ssh-keygen', '-i', '-m', sshtype, '-f', fname])
	except subprocess.CalledProcessError as e:
		raise
	finally:
		os.unlink(fname)

	return openssh_format.strip()

def rfc4716_to_openssh(ssh_key):
	return openssh_import('RFC4716', ssh_key)

def pkcs8_to_openssh(ssh_key):
	return openssh_import('PKCS8', ssh_key)

def pem_to_openssh(ssh_key):
	return openssh_import('PEM', ssh_key)
