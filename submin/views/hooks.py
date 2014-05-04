import os
from subprocess import CalledProcessError, STDOUT

from submin.dispatch.view import View
from submin.dispatch.response import XMLTemplateResponse
from submin.auth.decorators import acl_required, Unauthorized
from submin.common.execute import check_output
from submin.models.hookjobs import jobs, done as job_done
from submin.models import trac
from submin.models import options, repository

class Hooks(View):
	def handler(self, req, path):
		template = 'ajax/hooks.xml'
		tvars = {
			'command': '/'.join(path),
			'success': False,
			'inacl': True,
		}

		if len(path) < 1:
			tvars['errormsgs'] = ['path is incorrect']
			return XMLTemplateResponse(template, tvars)

		hook_type = path[0]
		try:
			subcmd_name = 'handle_%s' % (hook_type.replace('-', '_'))
			subcmd = getattr(self, subcmd_name)
		except AttributeError:
			tvars['errormsgs'] = ['unknown hook type']
			return XMLTemplateResponse(template, tvars)

		try:
			extra_vars = subcmd(path[1:])
		except Unauthorized, e:
			tvars['errormsgs'] = [str(e)]
			tvars['inacl'] = False
			return XMLTemplateResponse(template, tvars)
		
		tvars.update(extra_vars)
		return XMLTemplateResponse(template, tvars)

	@acl_required('acl_hook')
	def handle_trac_sync(self, path):
		if len(path) != 2:
			return {'errormsgs': ['wrong path']}

		self.vcs_type, self.repo = path

		errormsgs = []

		# migration from inconsistent usage of extension
		if self.repo.endswith('.git'):
			self.repo = self.repo[:-4]
			errormsgs.append(
				'Please let the submin administrator know to run diagnostics')

		self.env_copy = os.environ.copy()
		self.env_copy['PATH'] = options.value('env_path', '/bin:/usr/bin')
		trac_dir = options.env_path('trac_dir')
		repo_dir = repository.directory(self.vcs_type, self.repo)
		self.trac_env = trac_dir + self.repo

		oldwd = os.getcwd()
		try:
			os.chdir(repo_dir)
		except OSError, e:
			return {'errormsgs': ['Directory does not exist', str(e),
					'Please check Submin diagnostics'], 'success': False}

		for jobid, lines in jobs(self.vcs_type, self.repo, 'trac-sync'):
			job_succeeded = True

			errormsg = self.job_sync(jobid, lines)
			if len(errormsg) == 0:
				job_done(jobid)
			else:
				errormsgs.append(errormsg)

		os.chdir(oldwd)

		return {'errormsgs': errormsgs, 'success': True}

	def job_sync(self, jobid, lines):
		for line in lines.strip().split('\n'):
			try:
				oldrev, newrev, refname = line.split()
			except ValueError, e:
				return 'trac-sync/%s/%s/%s: %s' % (
					self.vcs_type, self.repo, jobid, str(e))

			cmd = ['git', 'rev-list', '--reverse', newrev, '^' + oldrev]
			if oldrev == '0' * 40:
				cmd.pop()

			try:
				revs = check_output(cmd, stderr=STDOUT, env=self.env_copy)
			except CalledProcessError, e:
				return 'cmd [%s] failed: %s', (cmd, e.output)

			for rev in revs.strip().split('\n'):
				args = ['changeset', 'added', '(default)', rev]
				output = trac.admin_command(self.trac_env, args)
				if output:
					return 'trac-admin %s: %s' % (' '.join(args), output)

		return []

