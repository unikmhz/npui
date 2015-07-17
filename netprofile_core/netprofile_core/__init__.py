#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Core module
# © Copyright 2013-2015 Alex 'Unik' Unigovsky
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

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_core')

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
		config.add_route('core.file.download', '/file/dl/{fileid:\d+}*filename', vhost='MAIN')
		config.add_route('core.file.upload', '/file/ul', vhost='MAIN')
		config.add_route('core.file.mount', '/file/mount/{ffid:\d+|root}*filename', vhost='MAIN')
		config.add_route('core.export', '/file/export/{module:[\w_.-]+}/{model:[\w_.-]+}', vhost='MAIN')

	@classmethod
	def get_models(cls):
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
			FileChunk,
			Tag,
			LogType,
			LogAction,
			LogData,
			NPSession,
			PasswordHistory,
			GlobalSetting,
			GlobalSettingSection,
			UserSetting,
			UserSettingSection,
			UserSettingType,
			DataCache,
			Calendar,
			CalendarImport,
			Event,
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
	def get_sql_data(cls, modobj, sess):
		from netprofile_core.models import UserState
		# FIXME: localization
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
			LogType(id=20, name='Folders')
		)
		for obj in log:
			sess.add(obj)
		sess.flush()

		grp_admins = Group(name='Administrators')
		sess.add(grp_admins)

		privs = (
			Privilege(
				code='BASE_ADMIN',
				name='Access: Administrative Tasks'
			),
			Privilege(
				code='BASE_USERS',
				name='Access: Users'
			),
			Privilege(
				code='BASE_GROUPS',
				name='Access: Groups'
			),
			Privilege(
				code='BASE_FILES',
				name='Access: Files'
			),
			Privilege(
				code='USERS_LIST',
				name='Users: List'
			),
			Privilege(
				code='USERS_CREATE',
				name='Users: Create',
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='USERS_EDIT',
				name='Users: Edit',
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='USERS_DELETE',
				name='Users: Delete',
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='USERS_GETCAP',
				name='Users: Display Capabilities'
			),
			Privilege(
				code='USERS_SETCAP',
				name='Users: Modify Capabilities',
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='USERS_GETACL',
				name='Users: Display ACLs'
			),
			Privilege(
				code='USERS_SETACL',
				name='Users: Set ACLs',
				has_acls=True,
				resource_class='NPUser'
			),
			Privilege(
				code='GROUPS_LIST',
				name='Groups: List'
			),
			Privilege(
				code='GROUPS_CREATE',
				name='Groups: Create',
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='GROUPS_EDIT',
				name='Groups: Edit',
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='GROUPS_DELETE',
				name='Groups: Delete',
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='GROUPS_GETCAP',
				name='Groups: Display Capabilities'
			),
			Privilege(
				code='GROUPS_SETCAP',
				name='Groups: Modify Capabilities',
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='GROUPS_GETACL',
				name='Groups: Display ACLs'
			),
			Privilege(
				code='GROUPS_SETACL',
				name='Groups: Set ACLs',
				has_acls=True,
				resource_class='NPGroup'
			),
			Privilege(
				code='FILES_LIST',
				name='Files: List'
			),
			Privilege(
				code='FILES_SHOWALL',
				name='Files: Full Access'
			),
			Privilege(
				code='FILES_UPLOAD',
				name='Files: Upload'
			),
			Privilege(
				code='FILES_DELETE',
				name='Files: Delete'
			),
			Privilege(
				code='FILES_EDIT',
				name='Files: Edit'
			),
			Privilege(
				code='PRIVILEGES_LIST',
				name='Privileges: List'
			),
			Privilege(
				code='PRIVILEGES_CREATE',
				name='Privileges: Create'
			),
			Privilege(
				code='PRIVILEGES_EDIT',
				name='Privileges: Edit'
			),
			Privilege(
				code='PRIVILEGES_DELETE',
				name='Privileges: Delete'
			),
			Privilege(
				code='SECPOL_LIST',
				name='Security Policies: List'
			),
			Privilege(
				code='SECPOL_CREATE',
				name='Security Policies: Create'
			),
			Privilege(
				code='SECPOL_EDIT',
				name='Security Policies: Edit'
			),
			Privilege(
				code='SECPOL_DELETE',
				name='Security Policies: Delete'
			)
		)
		for priv in privs:
			priv.module = modobj
			sess.add(priv)
		sess.flush()
		for priv in privs:
			cap = GroupCapability()
			cap.group = grp_admins
			cap.privilege = priv
			sess.add(cap)

		gss_admin = GlobalSettingSection( # no old id
			module=modobj,
			name='Administrative',
			description='Administrative settings.'
		)
		gss_vfs = GlobalSettingSection( # old id 8
			module=modobj,
			name='File System',
			description='Virtual File System setup.'
		)

		sess.add(gss_admin)
		sess.add(gss_vfs)

		uss_looknfeel = UserSettingSection( # old id 1
			module=modobj,
			name='Look and Feel',
			description='Basic settings for customizing NetProfile user interface.'
		)
		uss_locale = UserSettingSection( # old id 5
			module=modobj,
			name='Localization',
			description='Options related to language and regional settings.'
		)
		uss_outbox = UserSettingSection ( # old id 3
			module=modobj,
			name='Outgoing Messages',
			description='Configuration of protocol and server for outgoing messages.'
		)
		uss_inbox = UserSettingSection ( # old id 4
			module=modobj,
			name='Incoming Messages',
			description='Configuration of protocol and server for incoming messages.'
		)

		sess.add(uss_looknfeel)
		sess.add(uss_locale)
		sess.add(uss_outbox)
		sess.add(uss_inbox)

		ust_datagrid_perpage = UserSettingType(
			section=uss_looknfeel,
			module=modobj,
			name='datagrid_perpage',
			title='Number of elements per page',
			type='text',
			default='20',
			constraints={
				'cast'   : 'int',
				'minval' : 1,
				'maxval' : 200
			},
			description='Maximum number of rows to display on a single page of a table or grid.'
		)
		ust_datagrid_showrange = UserSettingType(
			section=uss_looknfeel,
			module=modobj,
			name='datagrid_showrange',
			title='Show result range',
			type='checkbox',
			default='true',
			description='Show current range of displayed entries in grid footer.'
		)
		ust_csv_charset = UserSettingType(
			section=uss_locale,
			module=modobj,
			name='csv_charset',
			title='CSV charset',
			type='text',
			default='UTF-8',
			description='Character set and encoding used when generating CSV files. Be warned that specifying non-unicode character set here can corrupt the data in the CSV.'
		)

		sess.add(ust_datagrid_perpage)
		sess.add(ust_datagrid_showrange)
		sess.add(ust_csv_charset)

		gs_login_allowed = GlobalSetting(
			section=gss_admin,
			module=modobj,
			name='login_allowed',
			title='Allow logging in',
			type='checkbox',
			value='true',
			default='true',
			description='Allow logging in to the user interface for non-admin users.'
		)
		gs_vfs_root_uid = GlobalSetting(
			section=gss_vfs,
			module=modobj,
			name='vfs_root_uid',
			title='Root User ID',
			type='text',
			value='1',
			default='1',
			constraints={
				'cast'   : 'int',
				'nullok' : False,
				'minval' : 0
			},
			description='User ID of the owner of the root folder.'
		)
		gs_vfs_root_gid = GlobalSetting(
			section=gss_vfs,
			module=modobj,
			name='vfs_root_gid',
			title='Root Group ID',
			type='text',
			value='1',
			default='1',
			constraints={
				'cast'   : 'int',
				'nullok' : False,
				'minval' : 0
			},
			description='Group ID of the owning group of the root folder.'
		)
		gs_vfs_root_rights = GlobalSetting(
			section=gss_vfs,
			module=modobj,
			name='vfs_root_rights',
			title='Root Rights',
			type='text',
			value='509',
			default='509',
			constraints={
				'cast'   : 'int',
				'nullok' : False,
				'minval' : 0,
				'maxval' : 1023
			},
			description='Bitmask specifying access rights for the root folder.'
		)

		sess.add(gs_login_allowed)
		sess.add(gs_vfs_root_uid)
		sess.add(gs_vfs_root_gid)
		sess.add(gs_vfs_root_rights)

		admin = User(
			group=grp_admins,
			state=UserState.active,
			login='admin',
			password='16lG71d3e58569b3e8730ad79ae7bd12a277defbc158',
			a1_hash='50c87497ceb6224572e2bce64611fcbc',
			enabled=True,
			name_given='Admin',
			name_family='User',
			title='Admin User'
		)

		sess.add(admin)

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
				'netprofile_core:static/extern/extensible/resources/css/extensible-all.css',
				'netprofile_core:static/css/main.css'
			)
		return (
			'netprofile_core:static/extern/extjs/build/packages/ext-theme-classic/build/resources/ext-theme-classic-all.css',
			'netprofile_core:static/extern/extensible/resources/css/extensible-all.css',
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

