from submin.models import storage as models_storage
storage = models_storage.get("hookjobs")

def jobs(repositorytype, repository, hooktype):
	return storage.jobs(repositorytype, repository, hooktype)

def queue(repositorytype, repository, hooktype, content):
	return storage.queue(repositorytype, repository, hooktype, content)

def done(jobid):
	return storage.done(jobid)

__doc__ = """
Storage contract
================

* jobs(repositorytype, repository, hooktype)
	Return a list of tuples [(jobid, content), ...] of jobs.

* queue(repositorytype, repository, hooktype, content)
	Queues a new job.

* done(jobid)
	Remove a job with id *jobid* from the queue.

"""
