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
from .dav import DAVPluginVFS

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_core')

def _int_fileid(info, request):
	info['match']['fileid'] = int(info['match']['fileid'])
	return True

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_core:locale/')
		mmgr.cfg.add_route('core.home', '/')
		mmgr.cfg.add_route('core.login', '/login')
		mmgr.cfg.add_route('core.logout', '/logout')
		mmgr.cfg.add_route('core.dav', '/dav*traverse', factory='netprofile.dav.DAVRoot')
		mmgr.cfg.scan()

	def add_routes(self, config):
		config.add_route('core.noop', '/noop')
		config.add_route('core.js.webshell', '/js/webshell')
		config.add_route('core.file.download', '/file/dl/{fileid:\d+}*filename',
				custom_predicates=(_int_fileid,))
		config.add_route('core.file.upload', '/file/ul')

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
			DataCache
		)

	def get_menus(self):
		return (
			Menu('modules', title=_('Modules'), order=10),
			Menu('settings', title=_('Settings'), order=20, direct='settings'),
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
			Menu('admin', title=_('Administration'), order=40, permission='BASE_ADMIN')
		)

	def get_js(self, request):
		if request.debug_enabled:
			return (
				'netprofile_core:static/extjs/ext-all-dev.js',
				'netprofile_core:static/sockjs/sockjs.js'
			)
		return (
			'netprofile_core:static/extjs/ext-all.js',
			'netprofile_core:static/sockjs/sockjs.min.js'
		)

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

	def get_dav_plugins(self, request):
		return {
			'fs' : DAVPluginVFS(request)
		}

	@property
	def name(self):
		return _('Core')

