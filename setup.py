#!/usr/bin/env python

from distutils.core import setup
from distutils.util import convert_path
import os
import sys
import glob
import fnmatch

def is_package(filename):
	return os.path.isdir(filename) \
			and os.path.isfile(os.path.join(filename, "__init__.py"))

# Taken from setuptools
def find_packages(directory, exclude=()):
	packages = []
	stack = [(convert_path(directory), '')]
	while stack:
		path, prefix = stack.pop(0)
		for name in os.listdir(path):
			filename = os.path.join(path, name)
			if '.' not in name and is_package(filename):
				packages.append(prefix + name)
				stack.append((filename, prefix + name + "."))

	for pattern in exclude:
		packages = [package for package in packages \
				if not fnmatch.fnmatchcase(package, pattern)]
	return packages

def find_data_files(directory, exclude_dirs=()):
	data_files = []
	for path, dirs, files in os.walk(directory):
		if any(fnmatch.fnmatchcase(path, pattern) for pattern in exclude_dirs):
			continue
		if files:
			share_name = path.replace(directory.rstrip(os.path.sep),
					"share/submin", 1) # Hack to force correct install path
			data_files.append((share_name,
				[os.path.join(path, name) for name in files]))
	return data_files

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
	packages=find_packages("packages", exclude=[".svn"]),
	package_dir={"submin": "packages/submin"},
	package_data={
		"submin": find_package_data("packages/submin/static", ["*.svn*"]),
	},
	data_files=[
		("share/man/man1", ("man/submin-admin.1",)),
	],
	scripts=["bin/submin-admin.py"],
)

