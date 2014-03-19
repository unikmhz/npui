#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Core module
# © Copyright 2013 Alex 'Unik' Unigovsky
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

from zope.interface.interfaces import ComponentLookupError

from netprofile.common.modules import ModuleBase
from netprofile.common.menus import Menu
from netprofile.dav import (
	IDAVManager,
	DAVRoot,
	DAVTraverser
)
from .models import *
from .dav import (
	DAVPluginVFS,
	DAVPluginUsers,
	DAVPluginGroups
)

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_core')

def _int_fileid(info, request):
	info['match']['fileid'] = int(info['match']['fileid'])
	return True

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		cfg = mmgr.cfg
		cfg.add_translation_dirs('netprofile_core:locale/')
		cfg.add_route('core.home', '/', vhost='MAIN')
		cfg.add_route('core.login', '/login', vhost='MAIN')
		cfg.add_route('core.logout', '/logout', vhost='MAIN')
		cfg.add_traverser(DAVTraverser, DAVRoot)
		cfg.add_route('core.dav', '/dav*traverse', factory='netprofile.dav.DAVRoot', vhost='MAIN')
		cfg.scan()

		try:
			dav = cfg.registry.getUtility(IDAVManager)
			if dav:
				dav.set_locks_backend(DAVLock)
		except ComponentLookupError:
			pass

	def add_routes(self, config):
		config.add_route('core.noop', '/noop', vhost='MAIN')
		config.add_route('core.js.webshell', '/js/webshell', vhost='MAIN')
		config.add_route('core.file.download', '/file/dl/{fileid:\d+}*filename',
				vhost='MAIN',
				custom_predicates=(_int_fileid,))
		config.add_route('core.file.upload', '/file/ul', vhost='MAIN')

	def get_models(self):
		return (
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
			DataCache,
			Calendar
		)

	def get_menus(self):
		return (
			Menu('modules', title=_('Modules'), order=10),
			Menu('users', title=_('Users'), order=20, direct='users', options={ # FIXME: add permission= ?
				'disableSelection' : True
			}),
			Menu('folders', title=_('Folders'), order=30, direct='folders', permission='FILES_LIST', options={
				'root'        : {
					'id'       : 'root',
					'text'     : _('Root Folder'),
					'xhandler' : 'NetProfile.controller.FileBrowser',
					'expanded' : True
				},
				'rootVisible' : True,
				'hideHeaders' : True,
				'columns'     : ({
					'xtype'     : 'treecolumn',
					'name'      : 'text',
					'dataIndex' : 'text',
					'flex'      : 1,
					'editable'  : True,
					'editor'    : {
						'xtype'      : 'textfield',
						'allowBlank' : False
					}
				},),
				'plugins'     : ({
					'ptype'    : 'manualediting',
					'pluginId' : 'editor'
				},),
				'useArrows'   : False,
				'viewConfig'  : {
					'plugins'   : ({
						'ptype'      : 'treeviewdragdrop',
						'ddGroup'    : 'ddFile',
						'appendOnly' : True
					},)
				}
			}, extra_fields=(
				{ 'name' : 'allow_read',     'type' : 'boolean' },
				{ 'name' : 'allow_write',    'type' : 'boolean' },
				{ 'name' : 'allow_traverse', 'type' : 'boolean' },
				{ 'name' : 'parent_write',   'type' : 'boolean' }
			)),
			Menu('settings', title=_('Settings'), order=40, direct='settings'),
			Menu('admin', title=_('Administration'), order=50, permission='BASE_ADMIN')
		)

	def get_js(self, request):
		if request.debug_enabled:
			return (
				'netprofile_core:static/extjs/ext-all-dev.js',
				'netprofile_core:static/extensible/lib/extensible-all-debug.js',
				'netprofile_core:static/tinymce/tiny_mce_src.js',
				'netprofile_core:static/sockjs/sockjs.js'
			)
		return (
			'netprofile_core:static/extjs/ext-all.js',
			'netprofile_core:static/extensible/lib/extensible-all.js',
			'netprofile_core:static/tinymce/tiny_mce.js',
			'netprofile_core:static/sockjs/sockjs.min.js'
		)

	def get_local_js(self, request, lang):
		return (
			'netprofile_core:static/extjs/locale/ext-lang-' + lang + '.js',
			'netprofile_core:static/extensible/src/locale/extensible-lang-' + lang + '.js',
			'netprofile_core:static/webshell/locale/webshell-lang-' + lang + '.js'
		)

	def get_css(self, request):
		return (
			'netprofile_core:static/extjs/resources/css/ext-all.css',
			'netprofile_core:static/extensible/resources/css/extensible-all.css',
			'netprofile_core:static/css/main.css'
		)

	def get_dav_plugins(self, request):
		return {
			'fs'     : DAVPluginVFS,
			'users'  : DAVPluginUsers,
			'groups' : DAVPluginGroups
		}

	@property
	def name(self):
		return _('Core')

