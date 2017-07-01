#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Core module
# © Copyright 2013-2017 Alex 'Unik' Unigovsky
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

import logging

from zope.interface.interfaces import ComponentLookupError
from sqlalchemy.orm.exc import NoResultFound

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

from netprofile.common.modules import ModuleBase
from netprofile.common.menus import Menu
from netprofile.common.settings import (
	Setting,
	SettingSection
)
from netprofile.dav import (
	IDAVManager,
	DAVRoot,
	DAVTraverser
)
from netprofile.export.csv import csv_encodings
from netprofile.common.crypto import (
	get_salt_string,
	hash_password
)

from .models import *
from .dav import (
	DAVPluginAddressBooks,
	DAVPluginGroups,
	DAVPluginUsers,
	DAVPluginVFS
)
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

logger = logging.getLogger(__name__)

_ = TranslationStringFactory('netprofile_core')

def _synctoken_cb(node):
	try:
		var = NPVariable.get_ro('DAV:SYNC:' + node.__dav_collid__)
	except NoResultFound:
		return 1
	if var:
		return var.integer_value

def _csv_encodings_menu(req, moddef, section, value):
	return {
		'xtype'          : 'combobox',
		'queryMode'      : 'local',
		'displayField'   : 'value',
		'valueField'     : 'id',
		'editable'       : False,
		'forceSelection' : True,
		'store'          : {
			'fields'  : ('id', 'value'),
			'sorters' : [{ 'property' : 'value', 'direction' : 'ASC' }],
			'data'    : [(k, v[1]) for k, v in csv_encodings.items()]
		},
		'value'          : value
	}

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		cfg = mmgr.cfg
		cfg.add_translation_dirs('netprofile_core:locale/')
		cfg.add_route('core.home', '/', vhost='MAIN')
		cfg.add_route('core.login', '/login', vhost='MAIN')
		cfg.add_route('core.logout', '/logout', vhost='MAIN')
		cfg.add_route('core.logout.direct', '/directlogout', vhost='MAIN')
		cfg.add_traverser(DAVTraverser, DAVRoot)
		cfg.add_route('core.dav', '/dav*traverse', factory='netprofile.dav.DAVRoot', vhost='MAIN')
		cfg.add_route('core.wellknown', '/.well-known/*service', vhost='MAIN')

		try:
			dav = cfg.registry.getUtility(IDAVManager)
			if dav:
				dav.set_locks_backend(DAVLock)
				dav.set_history_backend(DAVHistory)
				dav.set_sync_token_callback(_synctoken_cb)
		except ComponentLookupError:
			pass

	def add_routes(self, config):
		config.add_route('core.noop', '/noop', vhost='MAIN')
		config.add_route('core.about', '/about', vhost='MAIN')
		config.add_route('core.js.webshell', '/js/webshell', vhost='MAIN')
		config.add_route('core.file.download', '/file/dl/{fileid:\d+}*filename', vhost='MAIN')
		config.add_route('core.file.upload', '/file/ul', vhost='MAIN')
		config.add_route('core.file.mount', '/file/mount/{ffid:\d+|root}*filename', vhost='MAIN')
		config.add_route('core.export', '/file/export/{module:[\w_.-]+}/{model:[\w_.-]+}', vhost='MAIN')

	@classmethod
	def get_models(cls):
		return (
			NPModule,
			NPVariable,
			TaskSchedule,
			Task,
			TaskLog,
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
			FileChunk,
			Tag,
			LogType,
			LogAction,
			LogData,
			NPSession,
			PasswordHistory,
			GlobalSetting,
			UserSetting,
			DataCache,
			DAVLock,
			DAVHistory,
			Calendar,
			CalendarImport,
			Event,
			AddressBook,
			AddressBookCard,
			CommunicationType,
			UserCommunicationChannel,
			UserPhone,
			UserEmail
		)

	@classmethod
	def get_sql_functions(cls):
		return (
			HWAddrHexIEEEFunction,
			HWAddrHexLinuxFunction,
			HWAddrHexWindowsFunction,
			HWAddrUnhexFunction
		)

	@classmethod
	def get_sql_data(cls, modobj, vpair, sess):
		from netprofile_core.models import UserState

		if not vpair.is_install:
			return

		log = (
			LogAction(id=1, name='Created'),
			LogAction(id=2, name='Edited'),
			LogAction(id=3, name='Deleted'),
			LogAction(id=4, name='Copied'),
			LogAction(id=5, name='Moved'),
			LogAction(id=6, name='Renamed'),
			LogAction(id=7, name='Executed'),
			LogAction(id=8, name='Backed up'),
			LogAction(id=9, name='Restored from backup'),
			LogAction(id=10, name='Logged in'),
			LogAction(id=11, name='Logged out'),
			LogAction(id=12, name='Failed login'),

			LogType(id=1, name='Generic'),
			LogType(id=7, name='Users'),
			LogType(id=11, name='Groups'),
			LogType(id=17, name='Files'),
			LogType(id=20, name='Folders'),
			LogType(id=21, name='Global Settings'),
			LogType(id=22, name='Tasks')
		)
		for obj in log:
			sess.add(obj)
		sess.flush()

		grp_admins = Group(name='Administrators')
		sess.add(grp_admins)

		privs = (
			Privilege(
				code='BASE_ADMIN',
				name=_('Menu: Administrative tasks')
			),
			Privilege(
				code='BASE_USERS',
				name=_('Menu: Users')
			),
			Privilege(
				code='BASE_GROUPS',
				name=_('Menu: Groups')
			),
			Privilege(
				code='BASE_FILES',
				name=_('Menu: Files')
			),
			Privilege(
				code='BASE_TASKS',
				name=_('Menu: Periodic Tasks')
			),
			Privilege(
				code='ADMIN_SETTINGS',
				name=_('Administrative: Settings')
			),
			Privilege(
				code='ADMIN_SECURITY',
				name=_('Administrative: Security')
			),
			Privilege(
				code='ADMIN_MODULES',
				name=_('Administrative: Modules')
			),
			Privilege(
				code='ADMIN_DB',
				name=_('Administrative: Database ops')
			),
			Privilege(
				code='ADMIN_VFS',
				name=_('Administrative: File system')
			),
			Privilege(
				code='ADMIN_DEV',
				name=_('Administrative: Development')
			),
			Privilege(
				code='ADMIN_AUDIT',
				name=_('Administrative: Audit log')
			),
			Privilege(
				code='USERS_LIST',
				name=_('Users: List')
			),
			Privilege(
				code='USERS_CREATE',
				name=_('Users: Create'),
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='USERS_EDIT',
				name=_('Users: Edit'),
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='USERS_DELETE',
				name=_('Users: Delete'),
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='USERS_GETCAP',
				name=_('Users: Display capabilities')
			),
			Privilege(
				code='USERS_SETCAP',
				name=_('Users: Modify capabilities'),
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='USERS_GETACL',
				name=_('Users: Display ACLs')
			),
			Privilege(
				code='USERS_SETACL',
				name=_('Users: Set ACLs'),
				has_acls=True,
				resource_class='NPUser'
			),
			Privilege(
				code='GROUPS_LIST',
				name=_('Groups: List')
			),
			Privilege(
				code='GROUPS_CREATE',
				name=_('Groups: Create'),
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='GROUPS_EDIT',
				name=_('Groups: Edit'),
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='GROUPS_DELETE',
				name=_('Groups: Delete'),
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='GROUPS_GETCAP',
				name=_('Groups: Display capabilities')
			),
			Privilege(
				code='GROUPS_SETCAP',
				name=_('Groups: Modify capabilities'),
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='GROUPS_GETACL',
				name=_('Groups: Display ACLs')
			),
			Privilege(
				code='GROUPS_SETACL',
				name=_('Groups: Set ACLs'),
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='FILES_LIST',
				name=_('Files: List')
			),
			Privilege(
				code='FILES_SHOWALL',
				name=_('Files: Full access')
			),
			Privilege(
				code='FILES_UPLOAD',
				name=_('Files: Upload')
			),
			Privilege(
				code='FILES_DELETE',
				name=_('Files: Delete')
			),
			Privilege(
				code='FILES_EDIT',
				name=_('Files: Edit')
			),
			Privilege(
				code='TASKS_LIST',
				name=_('Tasks: List')
			),
			Privilege(
				code='TASKS_CREATE',
				name=_('Tasks: Create')
			),
			Privilege(
				code='TASKS_EDIT',
				name=_('Tasks: Edit')
			),
			Privilege(
				code='TASKS_DELETE',
				name=_('Tasks: Delete')
			),
			Privilege(
				code='PRIVILEGES_LIST',
				name=_('Privileges: List')
			),
			Privilege(
				code='PRIVILEGES_CREATE',
				name=_('Privileges: Create')
			),
			Privilege(
				code='PRIVILEGES_EDIT',
				name=_('Privileges: Edit')
			),
			Privilege(
				code='PRIVILEGES_DELETE',
				name=_('Privileges: Delete')
			),
			Privilege(
				code='SECPOL_LIST',
				name=_('Security Policies: List')
			),
			Privilege(
				code='SECPOL_CREATE',
				name=_('Security Policies: Create')
			),
			Privilege(
				code='SECPOL_EDIT',
				name=_('Security Policies: Edit')
			),
			Privilege(
				code='SECPOL_DELETE',
				name=_('Security Policies: Delete')
			)
		)
		for priv in privs:
			priv.module = modobj
			sess.add(priv)
		sess.flush()
		for priv in privs:
			if priv.code in {'ADMIN_DEV'}:
				continue
			cap = GroupCapability()
			cap.group = grp_admins
			cap.privilege = priv
			sess.add(cap)

		global_settings = (
			GlobalSetting(name='core.admin.login_allowed', value='true'),
			GlobalSetting(name='core.vfs.root_uid', value='1'),
			GlobalSetting(name='core.vfs.root_gid', value='1'),
			GlobalSetting(name='core.vfs.root_rights', value='509')
		)
		for gs in global_settings:
			sess.add(gs)

		pwd = get_salt_string(16)
		admin = User(
			group=grp_admins,
			state=UserState.active,
			login='admin',
			password=hash_password('admin', pwd),
			a1_hash=hash_password('admin', pwd, scheme='digest-ha1'),
			enabled=True,
			name_given='Admin',
			name_family='User',
			title='Admin User'
		)

		sess.add(admin)
		logger.critical('Generated initial administrative credentials: admin / %s', pwd)

		commtypes = (
			CommunicationType(
				name='SIP',
				icon='sip',
				uri_protocol='sip',
				description='Text/voice/video via SIP'
			),
			CommunicationType(
				name='Jabber/XMPP',
				icon='xmpp',
				uri_protocol='xmpp',
				uri_format='{proto}:{address}?roster',
				description='Text/voice/video via XMPP (includes Jabber and Google Talk)'
			),
			CommunicationType(
				name='IRC',
				icon='irc',
				uri_protocol='irc',
				uri_format='{proto}://{address}',
				description='Text chat via IRC'
			),
			CommunicationType(
				name='Yahoo! Messenger',
				icon='ymsgr',
				uri_protocol='ymsgr',
				uri_format='{proto}:addfriend?{address}',
				description='Text/voice/video via Yahoo! Messenger'
			),
			CommunicationType(
				name='Skype',
				icon='skype',
				uri_protocol='skype',
				description='Text/voice/video via Skype'
			),
			CommunicationType(
				name='AOL Instant Messenger',
				icon='aim',
				uri_protocol='aim',
				uri_format='{proto}:addbuddy?screenname={address}',
				description='Text/voice/video via AOL Instant Messenger'
			),
			CommunicationType(
				name='ICQ',
				icon='icq',
				uri_protocol='icq',
				uri_format='{proto}:message?uin={address}',
				description='Text/voice/video via AOL Instant Messenger'
			),
			CommunicationType(
				name='WhatsApp',
				icon='whatsapp',
				uri_protocol='whatsapp',
				uri_format='{proto}://send?abid={address}',
				description='Text/voice/video via WhatsApp'
			),
			CommunicationType(
				name='Viber',
				icon='viber',
				uri_protocol='viber',
				description='Text/voice/video via Viber'
			),
			CommunicationType(
				name='FaceTime',
				icon='facetime',
				uri_protocol='facetime',
				uri_format='{proto}://{address}',
				description='Voice/video via FaceTime'
			),
			CommunicationType(
				name='Apple iMessage',
				icon='imessage',
				uri_protocol='imessage',
				description='Text/voice/video via Apple iMessage'
			)
		)

		for obj in commtypes:
			sess.add(obj)

		gvars = (
			NPVariable(
				name='DAV:SYNC:ROOT',
				integer_value=1
			),
			NPVariable(
				name='DAV:SYNC:PLUG:VFS',
				integer_value=1
			),
			NPVariable(
				name='DAV:SYNC:PLUG:USERS',
				integer_value=1
			),
			NPVariable(
				name='DAV:SYNC:PLUG:GROUPS',
				integer_value=1
			),
			NPVariable(
				name='DAV:SYNC:PLUG:ABOOKS',
				integer_value=1
			),
			NPVariable(
				name='DAV:SYNC:PLUG:UABOOKS',
				integer_value=1
			)
		)
		for obj in gvars:
			sess.add(obj)

	def get_menus(self, request):
		loc = get_localizer(request)
		return (
			Menu('modules', title=loc.translate(_('Modules')), order=10),
			Menu('users', title=loc.translate(_('Users')), order=20, direct='users', options={ # FIXME: add permission= ?
				'disableSelection' : True
			}),
			Menu('folders', title=loc.translate(_('Folders')), order=30, direct='folders', permission='BASE_FILES', options={
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
					'ptype'    : 'cellediting',
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
			), custom_root={
				'id'       : 'root',
				'text'     : loc.translate(_('Root Folder')),
				'xhandler' : 'NetProfile.controller.FileBrowser',
				'expanded' : True
			}),
			Menu('settings', title=loc.translate(_('Settings')), order=40, direct='settings'),
			Menu('admin', title=loc.translate(_('Administration')), order=50, permission='BASE_ADMIN')
		)

	def get_js(self, request):
		if request.debug_enabled:
			return (
				'netprofile_core:static/extern/extjs/build/ext-all-debug.js',
				'netprofile_core:static/extern/extjs/build/packages/sencha-charts/build/sencha-charts-debug.js',
				'netprofile_core:static/extern/extjs/build/packages/ext-theme-classic/build/ext-theme-classic-debug.js',
				'netprofile_core:static/extern/extensible/lib/extensible-all-debug.js',
				# TODO: Upstream doesn't distribute unminified source.
				#       Might be a good idea to include it though.
				'netprofile_core:static/extern/tinymce/tinymce.min.js',
				'netprofile_core:static/extern/ipaddr/ipaddr.js',
				'netprofile_core:static/extern/sockjs/sockjs.js'
			)
		return (
			'netprofile_core:static/extern/extjs/build/ext-all.js',
			'netprofile_core:static/extern/extjs/build/packages/sencha-charts/build/sencha-charts.js',
			'netprofile_core:static/extern/extjs/build/packages/ext-theme-classic/build/ext-theme-classic.js',
			'netprofile_core:static/extensible/lib/extensible-all.js',
			'netprofile_core:static/extern/tinymce/tinymce.min.js',
			'netprofile_core:static/extern/ipaddr/ipaddr.min.js',
			'netprofile_core:static/extern/sockjs/sockjs.min.js'
		)

	def get_local_js(self, request, lang):
		return (
			'netprofile_core:static/extern/extjs/build/packages/ext-locale/build/ext-locale-' + lang + '.js',
			'netprofile_core:static/extern/extensible/src/locale/extensible-lang-' + lang + '.js',
			'netprofile_core:static/webshell/locale/webshell-lang-' + lang + '.js'
		)

	def get_css(self, request):
		if request.debug_enabled:
			return (
				'netprofile_core:static/extern/extjs/build/packages/ext-theme-classic/build/resources/ext-theme-classic-all-debug.css',
				'netprofile_core:static/extern/extjs/build/packages/sencha-charts/build/classic/resources/sencha-charts-all-debug.css',
				'netprofile_core:static/extern/extensible/resources/css/extensible-all.css',
				'netprofile_core:static/css/main.css'
			)
		return (
			'netprofile_core:static/extern/extjs/build/packages/ext-theme-classic/build/resources/ext-theme-classic-all.css',
			'netprofile_core:static/extern/extjs/build/packages/sencha-charts/build/classic/resources/sencha-charts-all.css',
			'netprofile_core:static/extern/extensible/resources/css/extensible-all.css',
			'netprofile_core:static/css/main.css'
		)

	def get_dav_plugins(self, request):
		return {
			'addressbooks' : DAVPluginAddressBooks,
			'fs'           : DAVPluginVFS,
			'groups'       : DAVPluginGroups,
			'users'        : DAVPluginUsers
		}

	def get_settings(self, vhost='MAIN', scope='global'):
		if vhost == 'MAIN' and scope == 'global':
			return (
				SettingSection(
					'admin',
					Setting(
						'login_allowed',
						title=_('Allow logging in'),
						help_text=_('Allow logging in to the user interface for non-admin users.'),
						type='bool',
						write_cap='ADMIN_SECURITY',
						default=True
					),
					title=_('Administrative'),
					help_text=_('Administrative settings.'),
					read_cap='BASE_ADMIN'
				),
				SettingSection(
					'vfs',
					Setting(
						'root_uid',
						title=_('Root User ID'),
						help_text=_('User ID of the owner of the root folder.'),
						type='int',
						default=1,
						write_cap='ADMIN_VFS',
						field_extra={ 'minValue' : 1 }
					),
					Setting(
						'root_gid',
						title=_('Root Group ID'),
						help_text=_('Group ID of the owning group of the root folder.'),
						type='int',
						default=1,
						write_cap='ADMIN_VFS',
						field_extra={ 'minValue' : 1 }
					),
					Setting(
						'root_rights',
						title=_('Root Rights'),
						help_text=_('Bitmask specifying access rights for the root folder.'),
						type='int',
						default=509,
						write_cap='ADMIN_VFS'
					),
					title=_('File System'),
					help_text=_('Virtual File System setup.'),
					read_cap='ADMIN_VFS'
				)
			)
		if vhost == 'MAIN' and scope == 'user':
			return (
				SettingSection(
					'ui',
					Setting(
						'datagrid_perpage',
						title=_('Number of elements per page'),
						help_text=_('Maximum number of rows to display on a single page of a table or grid.'),
						type='int',
						default=30,
						field_extra={ 'minValue' : 1, 'maxValue' : 200 }
					),
					Setting(
						'datagrid_showrange',
						title=_('Show result range'),
						help_text=_('Show current range of displayed entries in grid footer.'),
						type='bool',
						default=True
					),
					scope='user',
					title=_('Look and Feel'),
					help_text=_('Basic settings for customizing NetProfile user interface.')
				),
				SettingSection(
					'locale',
					Setting(
						'csv_charset',
						title=_('CSV charset'),
						help_text=_('Maximum number of rows to display on a single page of a table or grid.'),
						type='string',
						default='utf_8',
						field_cfg=_csv_encodings_menu
					),
					scope='user',
					title=_('Localization'),
					help_text=_('Options related to language and regional settings.')
				)
			)
		return ()

	@property
	def name(self):
		return _('Core')

