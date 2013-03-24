#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from netprofile.common.modules import ModuleBase
from netprofile.common.menus import Menu
from .models import *

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_core')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_core:locale/')
		mmgr.cfg.add_route('core.home', '/')
		mmgr.cfg.add_route('core.login', '/login')
		mmgr.cfg.add_route('core.logout', '/logout')
		mmgr.cfg.scan()

	def add_routes(self, config):
		config.add_route('core.noop', '/noop')
		config.add_route('core.js.webshell', '/js/webshell')

	def get_models(self):
		return [
			NPModule,
			User,
			Group,
			Privilege,
			UserCapability,
			GroupCapability,
			UserACL,
			GroupACL,
			UserGroup,
			SecurityPolicy,
			FileFolder,
			File,
			Tag,
			LogType,
			LogAction,
			LogData,
			NPSession,
			PasswordHistory,
			GlobalSettingSection,
			UserSettingSection,
			GlobalSetting,
			UserSettingType,
			UserSetting,
			DataCache
		]

	def get_menus(self):
		return (
			Menu('modules', title=_('Modules'), order=10),
			Menu('settings', title=_('Settings'), order=20, direct='settings'),
			Menu('admin', title=_('Administration'), order=30, permission='BASE_ADMIN')
		)

	def get_js(self, request):
		if request.debug_enabled:
			return ('netprofile_core:static/extjs/ext-all-dev.js',)
		return ('netprofile_core:static/extjs/ext-all.js',)

	def get_local_js(self, request, lang):
		return (
			'netprofile_core:static/extjs/locale/ext-lang-' + lang + '.js',
			'netprofile_core:static/webshell/locale/webshell-lang-' + lang + '.js'
		)

	def get_css(self, request):
		return (
			'netprofile_core:static/extjs/resources/css/ext-all.css',
			'netprofile_core:static/css/main.css'
		)

	@property
	def name(self):
		return _('Core')

