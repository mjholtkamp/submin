import os
import models
backends = models.vcs.list()

class Repository(object):
	@staticmethod
	def list():
		return []

	@staticmethod
	def add(name):
		pass

	def __init__(self, repositoryname=None):
		"Returns a Repository object"
		pass

	def remove(self):
		"Removes a Repository from disk (NO UNDO)"
		pass

	def subdirs(self, subdir):
		return []

__doc__ = """
Backend contract
================

Repository takes care of creating/deleting/listing repositories as well
as some secondary tasks.

* list()
	Returns a list of repositories

* add(name)
	Create a new repository with name *name*

* remove(name)
	Removes repository *name*

* subdirs(repository, subdir)
	Get a list of subdirs of repository *repository* and subdir *subdir*.
	Each dir is a dict with at least a property 'name'.
"""
