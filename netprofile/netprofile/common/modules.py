import pkg_resources
import logging

from zope.interface import (
	implementer,
	Interface
)

from netprofile.db.connection import DBSession
from netprofile.ext.data import ExtBrowser

logger = logging.getLogger(__name__)

class ModuleBase(object):
	"""
	Base class for NetProfile modules.
	"""

	@classmethod
	def version(cls):
		return (0, 0, 1)

	@classmethod
	def get_deps(cls):
		return []

	@classmethod
	def install(self):
		pass

	@classmethod
	def uninstall(self):
		pass

	def __init__(self, mmgr):
		pass

	def add_routes(self, config):
		pass

	def get_models(self):
		return []

	def get_menus(self):
		return []

	def get_js(self, request):
		return []

	def get_css(self, request):
		return []

	def load(self):
		pass

	def unload(self):
		pass

	@property
	def name(self):
		return self.__module__

class IModuleManager(Interface):
	"""
	Interface for NetProfile module manager.
	"""
	pass

@implementer(IModuleManager)
class ModuleManager(object):
	"""
	NetProfile module manager. Handles discovery, (un)loading
	and (un)installing modules.
	"""

	@classmethod
	def prepare(cls):
		"""
		Perform module discovery without loading all the discovered
		modules. Might be handy for various utility tasks.
		"""
		for ep in pkg_resources.iter_entry_points('netprofile.modules'):
			ep.load()

	def __init__(self, cfg):
		self.cfg = cfg
		self.modules = {}
		self.loaded = {}
		self.models = {}
		self.menus = {}

	def scan(self):
		"""
		Perform module discovery. Individual modules can't be loaded
		without this call.
		"""
		for ep in pkg_resources.iter_entry_points('netprofile.modules'):
			if ep.name in self.modules:
				continue
			mod = ep.load()
			if not issubclass(mod, ModuleBase):
				continue
			self.modules[ep.name] = mod

	def _load(self, moddef, mstack):
		"""
		Private method which actually loads a module.
		"""
		if (moddef in self.loaded) or (moddef in mstack):
			return True
		if moddef not in self.modules:
			logger.error('Can\'t find module \'%s\'. Verify installation and try again.', moddef)
			return False
		mstack.append(moddef)
		for depmod in self.modules[moddef].get_deps():
			if not self.load(depmod):
				logger.error('Can\'t load module \'%s\', which is needed for module \'%s\'.', depmod, moddef)
				return False
		mod = self.loaded[moddef] = self.modules[moddef](self)
		self.cfg.include(
			lambda conf: mod.add_routes(conf),
			route_prefix='/' + moddef
		)
		self.cfg.add_static_view(
			'static/' + moddef,
			self.modules[moddef].__module__ + ':static',
			cache_max_age=3600
		)
		self.models[moddef] = {}
		for model in mod.get_models():
			self._import_model(moddef, model)
		for menu in mod.get_menus():
			self.menus[menu.name] = menu
		return True

	def load(self, moddef):
		"""
		Load previously discovered module.
		"""
		mstack = []
		return self._load(moddef, mstack)

	def unload(self, moddef):
		"""
		Unload currently active module.
		"""
		pass

	def enable(self, moddef):
		"""
		Add a module to the list of enabled modules.
		"""
		pass

	def disable(self, moddef):
		"""
		Remove a module from the list of enabled modules.
		"""
		pass

	def load_enabled(self):
		"""
		Load all modules from enabled list. Must perform
		discovery first.
		"""
		from netprofile_core.models import NPModule

		sess = DBSession()
		for mod in sess.query(NPModule).filter(NPModule.enabled == True):
			self.load(mod.name)

	def install(self, moddef):
		"""
		Run module's installation hooks and register the module in DB.
		"""
		pass

	def uninstall(self, moddef):
		"""
		Unregister the module from DB and run module's uninstallation hooks.
		"""
		pass

	def _import_model(self, moddef, model):
		model.__moddef__ = moddef
		self.models[moddef][model.__name__] = model

	def get_module_browser(self):
		"""
		Get module traversal helper.
		"""
		return ExtBrowser(self)

	def get_js(self, request):
		"""
		Get a list of required JS file resources.
		"""
		l = []
		for moddef, mod in self.loaded.items():
			l.extend(mod.get_js(request))
		return l

	def get_css(self, request):
		"""
		Get a list of required CSS file resources.
		"""
		l = []
		for moddef, mod in self.loaded.items():
			l.extend(mod.get_css(request))
		return l

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	mmgr = ModuleManager(config)
	mmgr.scan()
	mmgr.load('core')
	mmgr.load_enabled()

	config.registry.registerUtility(mmgr, IModuleManager)

