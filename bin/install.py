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

class Main():
	def __init__(self):
		if len(sys.argv) < 2:
			self.usage()
			sys.exit(1)

		self.root = False
		if os.getuid() == 0:
			self.root = True

		self.prefix = sys.argv[1]
		self.final_prefix = self.prefix
		self.force = False
		for argv in sys.argv[2:]:
			if argv.startswith("--final="):
				self.final_prefix = argv[len("--final="):]

			if argv == "--force":
				self.force = True

		self.share = os.path.join(self.prefix, "share/submin")
		self.final_share = os.path.join(self.final_prefix, "share/submin")
		self.submin_admin = os.path.join(self.prefix, "bin/submin-admin")

		# check paths
		if (os.path.exists(self.share) or os.path.exists(self.submin_admin)) \
					and not self.force:
			print "Found previous installation at %s" % self.prefix
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
		print """
Usage: %s <installdir> [--force] [--final=<installdir2>]
	   --force     install, even if <installdir> exists
	   --replace   install into installdir, but prepare files because their
				   final installation directory is installdir2. This is used
				   for example by creating a debian package.
	""" % sys.argv[0]

	def filereplace(self, name, searchstring, replacestring):
		f = file(name, "r")
		lines = f.readlines()
		f.close()
		f = file(name, "w")
		for line in lines:
			f.write(line.replace(searchstring, replacestring))

	def copy_paths(self):
		self.dirname = os.path.dirname(sys.argv[0])
		srcdir = os.path.join(self.dirname, "..")
		os.chdir(srcdir)

		self.install("bin/submin-admin.py", self.submin_admin)

		if os.path.exists(self.share):
			shutil.rmtree(self.share)

		for d in ["css", "img", "js"]:
			shutil.copytree(os.path.join("www", d), \
							os.path.join(self.share, "www", d))

		for d in ["lib", "templates"]:
			shutil.copytree(d, os.path.join(self.share, d))

		for src in ["www/submin.wsgi", "www/submin.cgi"]:
			self.install(src, os.path.join(self.share, "www/"), mode=0755)
		for src in ["bin/commit-email.pl", "bin/post-commit.py"]:
			self.install(src, os.path.join(self.share, src), mode=0755)

		# fix hardcoded paths in binaries
		self.filereplace(self.submin_admin, "_SUBMIN_LIB_DIR_",
			os.path.join(self.final_share, "lib"))
		self.filereplace(os.path.join(self.share,
				"lib/subminadmin/subminadmin.py"),
			"_SUBMIN_SHARE_DIR_",
			self.final_share)
		self.filereplace(os.path.join(self.share, "bin/post-commit.py"),
			"_SUBMIN_LIB_DIR_",
			os.path.join(self.final_share, "lib"))

		self.remove_unwanted()

	def remove_unwanted(self):
		os.path.walk(self.share, self.remover, self)

	def remover(self, arg, dirname, names):
		if ".svn" in names:
			shutil.rmtree(os.path.join(dirname, ".svn"))
			del names[names.index(".svn")]

if __name__ == "__main__":
	main = Main()
	main.copy_paths()
