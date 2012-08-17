import pkg_resources

from zope.interface import (
	implementer,
	Interface
)

from netprofile.db.connection import DBSession
from netprofile.ext.data import ExtBrowser

class ModuleBase(object):

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

	def get_js(self):
		return []

	def get_css(self):
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

	@classmethod
	def prepare(cls):
		for ep in pkg_resources.iter_entry_points('netprofile.modules'):
			ep.load()

	def __init__(self, cfg):
		self.cfg = cfg
		self.modules = {}
		self.loaded = {}
		self.models = {}
		self.menus = {}
		self.res_js = []
		self.res_css = []

	def scan(self):
		for ep in pkg_resources.iter_entry_points('netprofile.modules'):
			if ep.name in self.modules:
				continue
			mod = ep.load()
			if not issubclass(mod, ModuleBase):
				continue
			self.modules[ep.name] = mod

	def load(self, moddef):
		if moddef in self.loaded:
			return True
		for depmod in self.modules[moddef].get_deps():
			self.load(depmod)
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
		self.res_js.extend(mod.get_js())
		self.res_css.extend(mod.get_css())
		return True

	def unload(self, moddef):
		pass

	def enable(self, moddef):
		pass

	def disable(self, moddef):
		pass

	def load_enabled(self):
		pass

	def install(self, moddef):
		pass

	def uninstall(self, moddef):
		pass

	def _import_model(self, moddef, model):
		model.__moddef__ = moddef
		self.models[moddef][model.__name__] = model

	def get_module_browser(self):
		return ExtBrowser(self)

def includeme(config):
	mmgr = ModuleManager(config)
	mmgr.scan()
	mmgr.load('core')
	mmgr.load_enabled()

	config.registry.registerUtility(mmgr, IModuleManager)

