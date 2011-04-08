#!/usr/bin/env python

from distutils.core import setup
from distutils.util import convert_path
import os
import sys
import glob
import fnmatch

def find_package_data(directory, exclude_dirs=()):
	data_files = []
	for path, dirs, files in os.walk(directory):
		if any(fnmatch.fnmatchcase(path, pattern) for pattern in exclude_dirs):
			continue
		if files:
			share_name = path.replace(directory.rstrip(os.path.sep),
					"static", 1) # Hack to force correct install path
			data_files += [os.path.join(share_name, name) for name in files]
	return data_files

def get_version():
	sys.path.append("packages")
	version = __import__("submin").VERSION
	sys.path.remove("packages")
	return version

setup(name='Submin',
	version=get_version(),
	description='Version Control System management',
	author='Michiel Holtkamp, Jean-Paul van Oosten',
	author_email='submin@webdevel.nl',
	url='http://www.supermind.nl/submin/',
	packages=["submin"],
	package_dir={"submin": "submin"},
	package_data={
		"submin": find_package_data("submin/static", ["*.svn*"]),
	},
	data_files=[
		("share/man/man1", ("man/submin2-admin.1",)),
	],
	scripts=["bin/submin2-admin"],
)

