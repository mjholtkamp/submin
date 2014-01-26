import os
from subprocess import CalledProcessError, STDOUT

from submin.dispatch.view import View
from submin.dispatch.response import XMLTemplateResponse
from submin.auth.decorators import acl_required, Unauthorized
from submin.common.execute import check_output
from submin.models.hookjobs import jobs, done as job_done
from submin.models.trac import trac_admin_command
from submin.models import options

class Hooks(View):
	def handler(self, req, path):
		template = 'ajax/hooks.xml'
		self.tvars = {
			'command': '/'.join(path),
			'success': False,
		}

		if len(path) != 3:
			self.tvars['errormsgs'] = ['path is incorrect']
			return XMLTemplateResponse(template, self.tvars)

		self.vcs_type, self.repo, self.hook_type = path[0:3]
		try:
			if self.hook_type == 'trac-sync':
				return self.handle_trac_sync()
			if self.hook_type == 'test-acl':
				return self.handle_test_acl()
		except Unauthorized, e:
			self.tvars['errormsgs'] = [str(e)]
			return XMLTemplateResponse(template, self.tvars)
		
		self.tvars['errormsgs'] = ['unknown hook type']
		return XMLTemplateResponse(template, self.tvars)

	@acl_required('acl_hook')
	def handle_test_acl(self):
		self.tvars['success'] = True
		return XMLTemplateResponse('ajax/hooks.xml', self.tvars)

	@acl_required('acl_hook')
	def handle_trac_sync(self):
		errormsgs = []
		env_copy = os.environ.copy()
		env_copy['PATH'] = options.value('env_path', '/bin:/usr/bin')
		trac_dir = options.env_path('trac_dir')
		repo_dir = options.env_path('git_dir') + self.repo
		trac_env = trac_dir + self.repo.replace('.git', '')

		oldwd = os.getcwd()
		os.chdir(repo_dir)
		for jobid, lines in jobs(self.vcs_type, self.repo, self.hook_type):
			job_succeeded = True

			errormsg = self.job_sync(lines, env_copy, trac_env)
			if len(errormsg) == 0:
				job_done(jobid)
			else:
				errormsgs.append(errormsg)

		os.chdir(oldwd)

		self.tvars['errormsgs'] = errormsgs
		self.tvars['success'] = True

		return XMLTemplateResponse('ajax/hooks.xml', self.tvars)

	def job_sync(self, lines, env_copy, trac_env):
		for line in lines.strip().split('\n'):
			try:
				oldrev, newrev, refname = line.split()
			except ValueError, e:
				return '%s/%s/%s/%s: %s' % (job,
					self.vcs_type, self.repo, self.hook_type, str(e))

			cmd = ['git', 'rev-list', '--reverse', newrev, '^' + oldrev]

			try:
				revs = check_output(cmd, stderr=STDOUT, env=env_copy)
			except CalledProcessError, e:
				return 'cmd [%s] failed: %s', (cmd, e.output)

			for rev in revs.strip().split('\n'):
				args = ['changeset', 'added', '(default)', rev]
				output = trac_admin_command(trac_env, args)
				if output:
					return 'trac-admin %s: %s' % (' '.join(args), output)

		return []

