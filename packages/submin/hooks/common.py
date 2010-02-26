import os
import glob
from subprocess import Popen

from submin.models import options

def trigger_hook(event, **args):
	#log(event, **args)
	# call our own hooks
	# first compose a list of all hooks
	from submin.hooks import system_hooks
	hooks = system_hooks.hooks.copy()

	for vcs_plugin in options.value('vcs_plugins').split(','):
		plugin_hooks = _get_vcs_plugin_hooks(vcs_plugin)
		for key in plugin_hooks:
			hooks[key] = hooks.get(key, []) + plugin_hooks[key]

	# Then execute all hooks
	if event in hooks:
		for hook_fn in hooks[event]:
			hook_fn(**args)

	trigger_user_hook(event, **args)

def _get_vcs_plugin_hooks(plugin):
	try:
		hooks_module = __import__("submin.plugins.vcs.%s.hooks" % plugin,
				globals(), locals(), ["submin.plugins.vcs.%s" % plugin])
		return hooks_module.hooks.copy()
	except (KeyError, ImportError):
		return {}

def trigger_user_hook(event, **args):
	user_hooks_path = options.env_path() + "hooks" + event
	if not user_hooks_path.exists():
		return

	user_hooks = glob.glob(str(user_hooks_path + "*"))
	user_hooks.sort()

	cwd = os.getcwd()
	os.chdir(str(options.env_path()))

	env = dict([(key.upper(), value) for key, value in args.iteritems()
			if value])
	for hook in user_hooks:
		try:
			# XXX What to do with system hooks which are not executable?
			# (since they are located in the site-packages directory)
			p = Popen([hook], env=env)
			p.wait() # wait for the hook to terminate
		except OSError, e:
			# XXX: log the error
			# log("An OS error occured while processing hook "
			# 	"%s. The error was: %s" % (hook, e))
			pass

	os.chdir(cwd)
