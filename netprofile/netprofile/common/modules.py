#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Module detection and loading
# © Copyright 2013-2016 Alex 'Unik' Unigovsky
#
# This file is part of NetProfile.
# NetProfile is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later
# version.
#
# NetProfile is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General
# Public License along with NetProfile. If not, see
# <http://www.gnu.org/licenses/>.

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import sys
import pkg_resources
import logging
import transaction

from zope.interface import (
	implementer,
	Interface
)

from packaging.requirements import Requirement
from packaging.version import parse
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm.exc import NoResultFound

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.ext.data import ExtBrowser
from netprofile.common.hooks import IHookManager
from netprofile.db.migrations import get_alembic_config

logger = logging.getLogger(__name__)

class ModuleBase(object):
	"""
	Base class for NetProfile modules.
	"""

	@classmethod
	def version(cls):
		dist = pkg_resources.get_distribution(cls.__module__)
		if dist:
			return parse(dist.version)

	@classmethod
	def get_deps(cls):
		return ()

	@classmethod
	def install(cls, sess):
		pass

	@classmethod
	def uninstall(cls, sess):
		pass

	@classmethod
	def upgrade(cls, sess, vpair):
		pass

	def __init__(self, mmgr):
		pass

	def add_routes(self, config):
		pass

	@classmethod
	def get_models(cls):
		return ()

	@classmethod
	def get_sql_functions(cls):
		return ()

	@classmethod
	def get_sql_views(cls):
		return ()

	@classmethod
	def get_sql_events(cls):
		return ()

	@classmethod
	def get_sql_data(cls, modobj, vpair, sess):
		pass

	def get_menus(self, request):
		return ()

	def get_js(self, request):
		return ()

	def get_local_js(self, request, lang):
		return ()

	def get_css(self, request):
		return ()

	def get_autoload_js(self, request):
		return ()

	def get_controllers(self, request):
		return ()

	def get_rt_handlers(self):
		return {}

	def get_rt_routes(self):
		return ()

	def get_dav_plugins(self, request):
		return {}

	def get_task_imports(self):
		return ()

	def load(self):
		pass

	def unload(self):
		pass

	def get_global_settings(self, request):
		pass

	def get_user_settings(self, request):
		pass

	@property
	def name(self):
		return self.__module__

class IModuleManager(Interface):
	"""
	Interface for NetProfile module manager.
	"""
	pass

class VersionPair(object):
	def __init__(self, old, new):
		if isinstance(old, str):
			old = parse(old)
		if isinstance(new, str):
			new = parse(new)
		self.old = old
		self.new = new

	@property
	def is_install(self):
		return self.old is None and self.new is not None

	@property
	def is_uninstall(self):
		return self.old is not None and self.new is None

	@property
	def is_upgrade(self):
		if self.old is None or self.new is None:
			return False
		return self.old < self.new

	@property
	def is_downgrade(self):
		if self.old is None or self.new is None:
			return False
		return self.old > self.new

	@property
	def is_noop(self):
		return self.old == self.new

	def is_upgrade_from(self, version):
		if not self.is_upgrade:
			return False
		if isinstance(version, str):
			version = parse(version)
		return version >= self.old

	def is_downgrade_to(self, version):
		if not self.is_downgrade:
			return False
		if isinstance(version, str):
			version = parse(version)
		return version >= self.new

class ModuleError(RuntimeError):
	pass

@implementer(IModuleManager)
class ModuleManager(object):
	"""
	NetProfile module manager. Handles discovery, (un)loading
	and (un)installing modules.
	"""

	def __init__(self, cfg, vhost=None, stdout=sys.stdout):
		self.cfg = cfg
		self.stdout = stdout
		self.modules = {}
		self.installed = None
		self.loaded = {}
		self.models = {}
		if vhost is None:
			sett = cfg.get_settings()
			self.vhost = sett.get('netprofile.vhost', None)
		else:
			self.vhost = vhost

	def scan(self):
		"""
		Perform module discovery. Individual modules can't be loaded
		without this call.
		"""
		mods = []
		for ep in pkg_resources.iter_entry_points('netprofile.modules'):
			if ep.name in self.modules:
				continue
			self.modules[ep.name] = ep
			mods.append(ep.name)

		return mods

	def rescan(self):
		"""
		Perform discovery of new modules at runtime. Does not reload modified
		modules or detect deleted ones.
		"""
		new_mods = []
		cur_env = pkg_resources.Environment(sys.path)
		dists, errors = pkg_resources.working_set.find_plugins(cur_env)
		for dist in dists:
			pname = dist.project_name
			if pname[:11] != 'netprofile-':
				continue
			moddef = pname[11:]
			if moddef in self.modules:
				continue
			new_mods.append(moddef)
			pkg_resources.working_set.add(dist)

		if len(new_mods) > 0:
			self.scan()

		return new_mods

	def _get_dist(self, moddef=None):
		"""
		Get distribution object for a module.
		"""
		if moddef is None:
			return pkg_resources.get_distribution('netprofile')
		return pkg_resources.get_distribution('netprofile_' + moddef)

	def _load(self, req, mstack, activate=True):
		"""
		Private method which actually loads a module.
		"""
		moddef = req.name
		modspec = req.specifier
		if moddef in mstack:
			# Try to prevent circular deps.
			return True
		if moddef in self.loaded:
			# Module is already loaded, need to only check version.
			curversion = self.loaded[moddef].version()
			if curversion not in modspec:
				logger.error(
					'Module \'%s\' version %s is already loaded, but required version is %s.',
					moddef, str(curversion), str(modspec)
				)
				return False
			return True
		if moddef not in self.modules:
			# Can't find module in installed Python packages.
			logger.error('Can\'t find module \'%s\'. Verify installation and try again.', moddef)
			return False
		if activate and not self.is_installed(req, DBSession()):
			if moddef != 'core':
				logger.error(
					'Can\'t load uninstalled/obsolete module \'%s\'. Please install/upgrade it first.',
					moddef
				)
			return False
		mstack.append(moddef)
		try:
			modcls = self.modules[moddef].load()
		except ImportError:
			logger.error('Can\'t load module \'%s\'. Verify installation and try again.', moddef)
			return False
		if not issubclass(modcls, ModuleBase):
			logger.error('Module \'%s\' is invalid. Verify installation and try again.', moddef)
			return False
		curversion = modcls.version()
		if curversion not in modspec:
			logger.error(
				'Module \'%s\' has version %s, but required version is %s.',
				moddef, str(curversion), str(modspec)
			)
			return False
		for depmod in modcls.get_deps():
			depreq = Requirement(depmod)
			if not self._load(depreq, mstack, activate=activate):
				logger.error('Can\'t load module \'%s\', which is needed for module \'%s\'.', depmod, moddef)
				return False
		mod = modcls(self)
		if activate:
			self.loaded[moddef] = mod
		self.cfg.include(
			lambda conf: mod.add_routes(conf),
			route_prefix='/' + moddef
		)
		# TODO: make cache_max_age configurable
		self.cfg.add_static_view(
			'static/' + moddef,
			self.modules[moddef].module_name + ':static',
			cache_max_age=3600
		)
		if activate:
			self.models[moddef] = {}
		mb = self.get_module_browser()
		hm = self.cfg.registry.getUtility(IHookManager)
		for model in mod.get_models():
			self._import_model(moddef, model, mb, hm, activate=activate)

		get_sql_functions = getattr(modcls, 'get_sql_functions', None)
		if callable(get_sql_functions):
			func_store = Base.metadata.info.setdefault('functions', set())
			for func in get_sql_functions():
				func.__moddef__ = moddef
				func_store.add(func)

		get_sql_views = getattr(modcls, 'get_sql_views', None)
		if callable(get_sql_views):
			view_store = Base.metadata.info.setdefault('views', set())
			for view in get_sql_views():
				view.__moddef__ = moddef
				view_store.add(view)

		get_sql_events = getattr(modcls, 'get_sql_events', None)
		if callable(get_sql_events):
			event_store = Base.metadata.info.setdefault('events', set())
			for evt in get_sql_events():
				evt.__moddef__ = moddef
				event_store.add(evt)

		return True

	def load(self, req):
		"""
		Load previously discovered module.
		"""
		mstack = []
		if not isinstance(req, Requirement):
			req = Requirement(req)
		return self._load(req, mstack)

	def preload(self, req):
		"""
		Discover module's data structures without loading it.
		"""
		mstack = []
		if not isinstance(req, Requirement):
			req = Requirement(req)
		return self._load(req, mstack, activate=False)

	def unload(self, req):
		"""
		Unload currently active module.
		"""
		raise NotImplementedError

	def enable(self, moddef):
		"""
		Add a module to the list of enabled modules.
		"""
		from netprofile_core.models import NPModule

		if moddef not in self.modules:
			logger.error('Can\'t find module \'%s\'. Verify installation and try again.', moddef)
			return False
		sess = DBSession()
		try:
			mod = sess.query(NPModule).filter(NPModule.name == moddef).one()
		except NoResultFound:
			return False
		if mod.enabled == True:
			return True
		mod.enabled = True
		transaction.commit()
		return self.load(moddef)

	def disable(self, moddef):
		"""
		Remove a module from the list of enabled modules.
		"""
		from netprofile_core.models import NPModule

		if moddef not in self.modules:
			logger.error('Can\'t find module \'%s\'. Verify installation and try again.', moddef)
			return False
		if moddef in self.loaded:
			if not self.unload(moddef):
				logger.error('Can\'t unload module \'%s\'.', moddef)
				return False
		sess = DBSession()
		try:
			mod = sess.query(NPModule).filter(NPModule.name == moddef).one()
		except NoResultFound:
			return False
		if mod.enabled == False:
			return True
		mod.enabled = False
		transaction.commit()
		return True

	def load_all(self):
		"""
		Load all modules disregarding whether they are enabled or not.
		Must perform discovery first.
		"""
		try:
			from netprofile_core.models import NPModule
		except ImportError:
			return False

		sess = DBSession()
		try:
			for mod in sess.query(NPModule):
				if mod.name != 'core':
					self.load(mod.name)
		except ProgrammingError:
			return False
		return True

	def load_enabled(self):
		"""
		Load all modules from enabled list. Must perform
		discovery first.
		"""
		try:
			from netprofile_core.models import NPModule
		except ImportError:
			return False

		sess = DBSession()
		try:
			for mod in sess.query(NPModule).filter(NPModule.enabled == True):
				if mod.name != 'core':
					self.load(mod.name)
		except ProgrammingError:
			return False
		return True

	def is_installed(self, req, sess):
		"""
		Check if a module is installed.
		"""
		if not isinstance(req, Requirement):
			req = Requirement(req)
		moddef = req.name
		modspec = req.specifier
		if ('core' not in self.loaded) and (moddef != 'core'):
			return False
		if moddef in self.loaded:
			return self.loaded[moddef].version() in modspec

		if self.installed is None:
			try:
				from netprofile_core.models import NPModule
			except ImportError:
				return False
			self.installed = dict()

			try:
				for mod in sess.query(NPModule):
					self.installed[mod.name] = mod.parsed_version
			except ProgrammingError:
				return False

		if moddef not in self.installed:
			return False
		return self.installed[moddef] in modspec

	# TODO: add circular dependency checking, like we do in _load()
	def install(self, req, sess, allow_upgrades=False):
		"""
		Run module's installation hooks and register the module in DB.
		"""
		from alembic import command
		from netprofile_core.models import NPModule

		if not isinstance(req, Requirement):
			req = Requirement(req)
		moddef = req.name
		modspec = req.specifier
		if ('core' not in self.loaded) and (moddef != 'core'):
			raise ModuleError('Unable to install anything prior to loading core module.')
		if self.is_installed(req, sess):
			if allow_upgrades and self.is_installed(Requirement(moddef), sess):
				return self.upgrade(req, sess)
			return False

		ep = self._find_ep(moddef)
		try:
			modcls = ep.load()
		except ImportError as e:
			raise ModuleError('Can\'t locate ModuleBase class for module \'%s\'.' % (moddef,)) from e

		modversion = self._cls_version(modcls)
		if modversion not in modspec:
			raise ModuleError('Module \'%s\' version %s can\'t satisfy requirements: %s.' % (
				moddef, str(modversion), str(modspec)
			))
		vpair = VersionPair(None, modversion)

		get_deps = getattr(modcls, 'get_deps', None)
		if callable(get_deps):
			for dep in get_deps():
				depreq = Requirement(dep)
				if not self.is_installed(depreq, sess):
					self.install(depreq, sess, allow_upgrades=allow_upgrades)

		modprep = getattr(modcls, 'prepare', None)
		if callable(modprep):
			modprep()

		if moddef != 'core':
			self.preload(moddef)

		get_models = getattr(modcls, 'get_models', None)
		if callable(get_models):
			tables = [model.__table__ for model in get_models()]
			Base.metadata.create_all(sess.bind, tables)

		get_sql_functions = getattr(modcls, 'get_sql_functions', None)
		if callable(get_sql_functions):
			for func in get_sql_functions():
				sess.execute(func.create(moddef))

		get_sql_views = getattr(modcls, 'get_sql_views', None)
		if callable(get_sql_views):
			for view in get_sql_views():
				sess.execute(view.create())

		modobj = NPModule(id=None)
		modobj.name = moddef
		modobj.current_version = str(modversion)
		if moddef == 'core':
			modobj.enabled = True
		sess.add(modobj)
		sess.flush()

		get_sql_data = getattr(modcls, 'get_sql_data', None)
		if callable(get_sql_data):
			get_sql_data(modobj, vpair, sess)

		mod_install = getattr(modcls, 'install', None)
		if callable(mod_install):
			mod_install(sess)

		if self.installed is None:
			self.installed = dict()
		self.installed[moddef] = modversion
		transaction.commit()

		get_sql_events = getattr(modcls, 'get_sql_events', None)
		if callable(get_sql_events):
			for evt in get_sql_events():
				sess.execute(evt.create(moddef))
			transaction.commit()

		alembic_cfg = get_alembic_config(self, stdout=self.stdout)
		command.stamp(alembic_cfg, moddef + '@head')
		transaction.commit()

		if moddef == 'core':
			self.load(moddef)
		return True

	# TODO: add circular dependency checking, like we do in _load()
	def upgrade(self, req, sess):
		"""
		Update DB schema, run module's upgrade hooks and register
		the new version in DB.
		"""
		from alembic import command
		from netprofile_core.models import NPModule

		if not isinstance(req, Requirement):
			req = Requirement(req)
		moddef = req.name
		modspec = req.specifier
		if ('core' not in self.loaded) and (moddef != 'core'):
			raise ModuleError('Unable to upgrade anything prior to loading core module.')
		if not self.is_installed(Requirement(moddef), sess):
			raise ModuleError('Can\'t upgrade uninstalled module \'%s\', use install command instead.' % (moddef,))

		ep = self._find_ep(moddef)
		try:
			modcls = ep.load()
		except ImportError as e:
			raise ModuleError('Can\'t locate ModuleBase class for module \'%s\'.' % (moddef,)) from e

		new_modversion = self._cls_version(modcls)
		modobj = sess.query(NPModule).filter(NPModule.name == moddef).one()
		old_modversion = modobj.parsed_version
		if old_modversion not in modspec:
			raise ModuleError('Module \'%s\' version %s can\'t satisfy requirements: %s.' % (
				moddef, str(old_modversion), str(modspec)
			))
		if old_modversion >= new_modversion:
			return False
		vpair = VersionPair(old_modversion, new_modversion)

		get_deps = getattr(modcls, 'get_deps', None)
		if callable(get_deps):
			for dep in get_deps():
				depreq = Requirement(dep)
				if not self.is_installed(depreq, sess):
					self.install(depreq, sess, allow_upgrades=True)

		modprep = getattr(modcls, 'prepare', None)
		if callable(modprep):
			modprep()

		if moddef != 'core':
			self.preload(moddef)

		alembic_cfg = get_alembic_config(self, stdout=self.stdout)
		command.upgrade(alembic_cfg, moddef + '@head')

		modobj.current_version = str(new_modversion)
		sess.flush()
		get_sql_data = getattr(modcls, 'get_sql_data', None)
		if callable(get_sql_data):
			get_sql_data(modobj, vpair, sess)
		transaction.commit()

		mod_upgrade = getattr(modcls, 'upgrade', None)
		if callable(mod_upgrade):
			mod_upgrade(sess, vpair)

		if moddef == 'core':
			self.load(moddef)
		return True

	def uninstall(self, req, sess):
		"""
		Unregister the module from DB and run module's uninstallation hooks.
		"""
		from netprofile_core.models import NPModule

		if not isinstance(req, Requirement):
			req = Requirement(req)
		moddef = req.name
		modspec = req.specifier
		if ('core' not in self.loaded) and (moddef != 'core'):
			raise ModuleError('Unable to uninstall anything prior to loading core module.')
		if not self.is_installed(req, sess):
			return False

		mod_uninstall = getattr(modcls, 'uninstall', None)
		if callable(mod_uninstall):
			mod_uninstall(sess)
		# FIXME: write this
		transaction.commit()

		return True

	def assert_loaded(self, *mods):
		if (len(mods) == 1) and isinstance(mods[0], (list, tuple, set)):
			mods = mods[0]
		not_loaded = set(mods) - set(self.loaded)
		if len(not_loaded) > 0:
			raise ModuleError('These modules aren\'t loaded, but are required: %s.' % (', '.join(not_loaded),))

	def _find_ep(self, moddef):
		if moddef in self.modules:
			return self.modules[moddef]
		match = list(pkg_resources.iter_entry_points('netprofile.modules', moddef))
		if len(match) == 0:
			raise ModuleError('Can\'t find module: \'%s\'.' % (moddef,))
		if len(match) > 1:
			raise ModuleError('Can\'t resolve module to single distribution: \'%s\'.' % (moddef,))
		ep = match[0]
		if ep.name != moddef:
			raise ModuleError('Loaded module source \'%s\', but was asked to load \'%s\'.' % (
				ep.name, moddef
			))
		self.modules[moddef] = ep
		return ep

	def _cls_version(self, modcls):
		modv = getattr(modcls, 'version', None)
		if callable(modv):
			return modv()
		return parse('0')

	def _import_model(self, moddef, model, mb, hm, activate=True):
		mname = model.__name__
		model.__moddef__ = moddef
		if activate:
			self.models[moddef][mname] = model
			hm.run_hook('np.model.load', self, mb[moddef][mname])

	def get_module_browser(self):
		"""
		Get module traversal helper.
		"""
		return ExtBrowser(self)

	def get_export_formats(self):
		"""
		Get registered data export formats.
		"""
		ret = {}
		for ep in pkg_resources.iter_entry_points('netprofile.export.formats'):
			try:
				cls = ep.load()
				ret[ep.name] = cls()
			except ImportError:
				logger.error('Can\'t load export formatter \'%s\'.', moddef)
		return ret

	def get_export_format(self, name):
		"""
		Get registered data export format by name.
		"""
		eps = tuple(pkg_resources.iter_entry_points('netprofile.export.formats', name))
		if len(eps) == 0:
			raise ModuleError('Can\'t load export formatter \'%s\'.' % (name,))
		try:
			cls = eps[0].load()
			return cls()
		except ImportError:
			raise ModuleError('Can\'t load export formatter \'%s\'.' % (name,))

	def get_js(self, request):
		"""
		Get a list of required JS file resources.
		"""
		l = []
		for moddef, mod in self.loaded.items():
			l.extend(mod.get_js(request))
		return l

	def get_local_js(self, request, lang):
		"""
		Get a list of required localization JS file resources.
		"""
		l = []
		for moddef, mod in self.loaded.items():
			l.extend(mod.get_local_js(request, lang))
		return l

	def get_css(self, request):
		"""
		Get a list of required CSS file resources.
		"""
		l = []
		for moddef, mod in self.loaded.items():
			l.extend(mod.get_css(request))
		return l

	def get_autoload_js(self, request):
		"""
		Get a list of JS classes to be autoloaded on client.
		"""
		l = []
		for moddef, mod in self.loaded.items():
			l.extend(mod.get_autoload_js(request))
		return l

	def get_controllers(self, request):
		"""
		Get a list of ExtJS classes to use as MVC controllers.
		"""
		l = []
		for moddef, mod in self.loaded.items():
			l.extend(mod.get_controllers(request))
		return l

	def get_rt_handlers(self, request):
		"""
		Get a dict of all realtime event handlers.
		"""
		ret = {}
		for moddef, mod in self.loaded.items():
			ret.update(mod.get_rt_handlers())
		return ret

	def get_rt_routes(self):
		"""
		Get a list of all additional realtime routes.
		"""
		l = []
		for moddef, mod in self.loaded.items():
			l.extend(mod.get_rt_routes())
		return l

	def get_dav_plugins(self, request):
		"""
		Get a dict of all DAV plugins.
		"""
		ret = {}
		for moddef, mod in self.loaded.items():
			ret.update(mod.get_dav_plugins(request))
		return ret

	def get_task_imports(self):
		"""
		Get a list of all modules containing Celery tasks.
		"""
		ret = []
		for moddef, mod in self.loaded.items():
			ret.extend(mod.get_task_imports())
		return ret

	def get_global_settings(self, request):
		"""
		Get a dict of all global settings of all modules.
		"""
		return dict((moddef, mod.get_global_settings(request))
			for moddef, mod
			in self.loaded.items()
		)

	def get_user_settings(self, request):
		"""
		Get a dict of all user settings of all modules.
		"""
		return dict((moddef, mod.get_user_settings(request))
			for moddef, mod
			in self.loaded.items()
		)

	def menu_generator(self, request):
		"""
		Generate all registered UI menu objects.
		"""
		for moddef, mod in self.loaded.items():
			for menu in mod.get_menus(request):
				menu.__moddef__ = moddef
				yield menu

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""

	config.add_translation_dirs('netprofile:locale/')

	mmgr = ModuleManager(config)
	mmgr.scan()

	config.registry.registerUtility(mmgr, IModuleManager)

