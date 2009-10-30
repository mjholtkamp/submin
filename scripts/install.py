#!/usr/bin/python
#
# Install files in the proper directories. Not shown in usage, but 
# if you provide two arguments it will install in the first prefix,
# but changes files because they will be ultimately installed in the
# second prefix. This is implemented so that files can be installed in
# a temporary directory used for packaging (i.e. debian package), but
# are ultimately installed in another.
#
# If any second argument is given, it will force install

import os
import sys
import shutil

class Main(object):
	def __init__(self):
		if len(sys.argv) < 3:
			self.usage()
			sys.exit(1)

		self.root = False
		if os.getuid() == 0:
			self.root = True

		self.prefix = sys.argv[1]
		self.python_dest_dir = sys.argv[2]
		self.final_prefix = self.prefix
		self.force = False
		for argv in sys.argv[2:]:
			if argv == "--force":
				self.force = True

		self.share = os.path.join(self.prefix, "share/submin")
		self.submin_admin = os.path.join(self.prefix, "bin/submin-admin")

		# check paths
		if (os.path.exists(self.share) or os.path.exists(self.submin_admin) \
					or os.path.exists(self.python_dest_dir)) \
					and not self.force:
			print "Found previous installation in one of these places:"
			to_be_deleted = [self.share, self.python_dest_dir]
			for dir in to_be_deleted:
				print "  ", dir
			print
				
			print "To overwrite use: ",
			for argv in sys.argv:
				print argv,
			print "--force"
			sys.exit(1)

	def install(self, src, dst, mode=0644, uid=0, gid=0):
		# if dst is a dir, append src filename, this is mainly for 
		# chmod/chown later
		if os.path.isdir(dst):
			dst = os.path.join(dst, os.path.basename(src))

		dirname = os.path.dirname(dst)
		if not os.path.exists(dirname):
			os.makedirs(dirname)

		shutil.copy(src, dst)
		os.chmod(dst, mode)
		if self.root:
			os.chown(dst, uid, gid)

	def usage(self):
		print """Usage: %s <prefix> <python-dir> [--force]

   Install static files in <prefix>/share/man, <prefix>/share/submin and
   <prefix>/bin. Install python modules in <python-dir> (whole path needed).

Example values:
       <prefix>     /usr
       <python-dir> /usr/local/pythonX.Y/python-submin

Options:
       --force      install, even if <installdir> exists
	""" % sys.argv[0]

	def copy_paths(self):
		if self.force:
			try:
				shutil.rmtree(self.share)
			except OSError:
				pass
			try:
				shutil.rmtree(self.python_dest_dir)
			except OSError:
				pass

		self.dirname = os.path.dirname(sys.argv[0])
		srcdir = os.path.join(self.dirname, "..")
		os.chdir(srcdir)

		self.install("bin/submin-admin.py", self.submin_admin)

		if os.path.exists(self.share):
			shutil.rmtree(self.share)

		for d in ["www", "templates", "hooks"]:
			shutil.copytree(os.path.join("static", d), \
							os.path.join(self.share, d))

		shutil.copytree("packages/submin", self.python_dest_dir)

#		for src in ["www/submin.wsgi", "www/submin.cgi"]:
#			self.install(src, os.path.join(self.share, "www/"), mode=0755)
#		for src in ["bin/svn/commit-email.pl", "bin/svn/post-commit.py"]:
#			self.install(src, os.path.join(self.share, src), mode=0755)

		self.remove_unwanted()

	def remove_unwanted(self):
		os.path.walk(self.share, self.remover, self)
		os.path.walk(self.python_dest_dir, self.remover, self)

	def remover(self, arg, dirname, names):
		if ".svn" in names:
			shutil.rmtree(os.path.join(dirname, ".svn"))
			del names[names.index(".svn")]

if __name__ == "__main__":
	main = Main()
	main.copy_paths()
