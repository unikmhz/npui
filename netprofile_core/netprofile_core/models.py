#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Core module - Modules
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

__all__ = [
	'NPModule',
	'UserState',
	'User',
	'Group',
	'Privilege',
	'Capability',
	'UserCapability',
	'GroupCapability',
	'ACL',
	'UserACL',
	'GroupACL',
	'UserGroup',
	'SecurityPolicyOnExpire',
	'SecurityPolicy',
	'FileFolderAccessRule',
	'FileFolder',
	'File',
	'FileChunk',
	'Tag',
	'LogType',
	'LogAction',
	'LogData',
	'NPSession',
	'PasswordHistory',
	'GlobalSettingSection',
	'UserSettingSection',
	'GlobalSetting',
	'UserSettingType',
	'UserSetting',
	'DataCache',
	'DAVLock',
	'Calendar',
	'CalendarImport',
	'Event',

	'HWAddrHexIEEEFunction',
	'HWAddrHexLinuxFunction',
	'HWAddrHexWindowsFunction',
	'HWAddrUnhexFunction',

	'global_setting'
]

import io
import errno
import string
import random
import re
import hashlib
import datetime as dt
import urllib
import itertools
import base64
import icalendar

from sqlalchemy import (
	BINARY,
	Column,
	FetchedValue,
	ForeignKey,
	Index,
	LargeBinary,
	PickleType,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	event,
	func,
	text,
	or_,
	and_
)

from sqlalchemy.orm import (
	backref,
	deferred,
	joinedload,
	relationship,
	validates
)

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound

from netprofile import (
	PY3,
	inst_id
)
from netprofile.common import (
	ipaddr,
	cal
)
from netprofile.common.phps import HybridPickler
from netprofile.common.threadlocal import magic
from netprofile.common.cache import cache
from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIFixedString,
	ASCIIString,
	DeclEnum,
	ExactUnicode,
	Int8,
	IPv4Address,
	IPv6Address,
	LargeBLOB,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	npbool
)
from netprofile.ext.wizards import (
	ExtJSWizardField,
	SimpleWizard,
	Step,
	Wizard
)
from netprofile.ext.columns import MarkupColumn
from netprofile.dav import (
	IDAVFile,
	IDAVCollection,
	IDAVPrincipal,

	DAVAllPropsSet,
	DAVACEValue,
	DAVACLValue,
	DAVPrincipalValue,
	DAVResourceTypeValue,

	dprops
)
from netprofile.ext.filters import (
	SelectFilter
)
from netprofile.db.ddl import (
	Comment,
	CurrentTimestampDefault,
	SQLFunction,
	SQLFunctionArgument,
	Trigger
)

from pyramid.response import (
	FileIter,
	Response
)
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)
from pyramid.security import (
	Allow, Deny,
	Everyone, Authenticated,
	DENY_ALL,
	has_permission
)
from zope.interface import implementer

_ = TranslationStringFactory('netprofile_core')

_DEFAULT_DICT = 'netprofile_core:dicts/np_cmb_rus'

F_OWNER_READ  = 0x0100
F_OWNER_WRITE = 0x0080
F_OWNER_EXEC  = 0x0040
F_GROUP_READ  = 0x0020
F_GROUP_WRITE = 0x0010
F_GROUP_EXEC  = 0x0008
F_OTHER_READ  = 0x0004
F_OTHER_WRITE = 0x0002
F_OTHER_EXEC  = 0x0001

F_OWNER_ALL   = 0x01c0
F_GROUP_ALL   = 0x0038
F_OTHER_ALL   = 0x0007
F_RIGHTS_ALL  = 0x01ff

F_DEFAULT_FILES = F_OWNER_READ | F_OWNER_WRITE | F_GROUP_READ | F_GROUP_WRITE | F_OTHER_READ
F_DEFAULT_DIRS = F_OWNER_ALL | F_GROUP_ALL | F_OTHER_READ | F_OTHER_EXEC

_VFS_READ     = 0x01
_VFS_WRITE    = 0x02
_VFS_APPEND   = 0x04
_VFS_TRUNCATE = 0x10

def _gen_xcap(cls, k, v):
	"""
	Creator for privilege-related attribute-mapped collections.
	"""
	priv = DBSession.query(Privilege).filter(Privilege.code == k).one()
	if priv is None:
		raise KeyError('Unknown privilege %s' % k)
	return cls(privilege=priv, value=v)

def _gen_xacl(cls, k, v):
	"""
	Creator for ACL-related attribute-mapped collections.
	"""
	priv = DBSession.query(Privilege).filter(Privilege.code == k[0]).one()
	if priv is None:
		raise KeyError('Unknown privilege %s' % k[0])
	return cls(privilege=priv, resource=k[1], value=v)

def _gen_user_setting(k, v):
	"""
	Creator for user-setting-related attribute-mapped collections.
	"""
	ust = DBSession.query(UserSettingType).filter(UserSettingType.name == k).one()
	return UserSetting(type=ust, value=ust.param_to_db(v))

class NPModule(Base):
	"""
	NetProfile module registry.
	"""
	__tablename__ = 'np_modules'
	__table_args__ = (
		Comment('NetProfile modules'),
		Index('np_modules_u_name', 'name', unique=True),
		Index('np_modules_i_enabled', 'enabled'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : 'BASE_ADMIN',

				'show_in_menu' : 'admin',
				'menu_name'    : _('Modules'),
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('npmodid', 'name', 'curversion', 'enabled'),
				'grid_hidden'  : ('npmodid',),
				'easy_search'  : ('name',)
			}
		}
	)
	id = Column(
		'npmodid',
		UInt32(),
		Sequence('np_modules_npmodid_seq'),
		Comment('NetProfile module ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('NetProfile module name'),
		nullable=False,
		default=None,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	current_version = Column(
		'curversion',
		ASCIIString(32),
		Comment('NetProfile module current version'),
		nullable=False,
		default='0.0.1',
		server_default='0.0.1',
		info={
			'header_string' : _('Version'),
			'column_flex'   : 1
		}
	)
	enabled = Column(
		NPBoolean(),
		Comment('Is module enabled?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Enabled')
		}
	)

	privileges = relationship(
		'Privilege',
		backref=backref('module', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	global_sections = relationship(
		'GlobalSettingSection',
		backref=backref('module', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	user_sections = relationship(
		'UserSettingSection',
		backref=backref('module', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	global_settings = relationship(
		'GlobalSetting',
		backref=backref('module', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	user_setting_types = relationship(
		'UserSettingType',
		backref=backref('module', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __init__(self, id=id, name=None, current_version='1.0.0', enabled=False):
		self.id = id
		self.name = name
		self.current_version = current_version
		self.enabled = enabled

	def __repr__(self):
		return 'NPModule(%s,%s,%s,%s)' % (
			repr(self.id),
			repr(self.name),
			repr(self.current_version),
			repr(self.enabled)
		)

	def __str__(self):
		return '%s' % str(self.name)

	def get_tree_node(self, req, mod):
		loc = get_localizer(req)
		return {
			'id'       : self.name,
			'text'     : loc.translate(mod.name),
			'leaf'     : False,
			'expanded' : True,
			'iconCls'  : 'ico-module'
		}

class UserState(DeclEnum):
	"""
	Current user state ENUM.
	"""
	pending = 'P', _('Pending'), 10
	active  = 'A', _('Active'),  20
	deleted = 'D', _('Deleted'), 30

def _validate_user_password(model, colname, values, req):
	if colname not in values:
		return
	try:
		uid = int(values['uid'])
	except (KeyError, TypeError, ValueError):
		return
	sess = DBSession()
	user = sess.query(User).get(uid)
	if user is None:
		return
	newpwd = values[colname]
	if newpwd is None:
		return
	secpol = user.effective_policy
	if secpol is None:
		return
	ts = dt.datetime.now()
	checkpw = secpol.check_new_password(req, user, newpwd, ts)
	if checkpw is True:
		return
	loc = get_localizer(req)
	return secpol_errors(checkpw, loc)

def secpol_errors(checkpw, loc):
	errors = []
	if 'pw_length_min' in checkpw:
		errors.append(loc.translate(_('Password is too short.')))
	if 'pw_length_max' in checkpw:
		errors.append(loc.translate(_('Password is too long.')))
	if 'pw_ctype_min' in checkpw:
		errors.append(loc.translate(_('Password has not enough character types.')))
	if 'pw_ctype_max' in checkpw:
		errors.append(loc.translate(_('Password has too many character types.')))
	if 'pw_dict_check' in checkpw:
		errors.append(loc.translate(_('Password was found in a dictionary.')))
	if 'pw_hist_check' in checkpw:
		errors.append(loc.translate(_('You used this password not too long ago.')))
	if 'pw_age_min' in checkpw:
		errors.append(loc.translate(_('You\'ve just changed your password.')))
	return errors

@implementer(IDAVFile, IDAVPrincipal)
class User(Base):
	"""
	NetProfile operator user.
	"""
	__tablename__ = 'users'
	__table_args__ = (
		Comment('Users'),
		Index('users_u_login', 'login', unique=True),
		Index('users_i_gid', 'gid'),
		Index('users_i_secpolid', 'secpolid'),
		Index('users_i_state', 'state'),
		Index('users_i_enabled', 'enabled'),
		Index('users_i_managerid', 'managerid'),
		Index('users_i_photo', 'photo'),
		Trigger('after', 'insert', 't_users_ai'),
		Trigger('after', 'update', 't_users_au'),
		Trigger('after', 'delete', 't_users_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_USERS',
				'cap_read'     : 'USERS_LIST',
				'cap_create'   : 'USERS_CREATE',
				'cap_edit'     : 'USERS_EDIT',
				'cap_delete'   : 'USERS_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : _('Users'),
				'default_sort' : ({ 'property': 'login' ,'direction': 'ASC' },),
				'grid_view'    : ('uid', 'login', 'name_family', 'name_given', 'name_middle', 'manager', 'group', 'enabled', 'state', 'security_policy', 'email'),
				'grid_hidden'  : ('uid', 'name_middle', 'manager', 'security_policy'),
				'form_view'    : (
					'login', 'name_family', 'name_given', 'name_middle',
					'title', 'group', 'secondary_groups', 'enabled',
					'pass', 'security_policy', 'state',
					'email', 'manager', 'photo'
				),
				'easy_search'  : ('login', 'name_family'),
				'create_wizard' : 
					Wizard(
						Step('login', 'pass', 'group', 'email', title=_('New user')),
						Step('name_family', 'name_given', 'name_middle', 'ipaddr', 'enabled','state',title=_('New user details')),
						title=_('Add new user')
					),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple'),
				'ldap_classes' : ('npUser', 'posixAccount', 'shadowAccount'),
				'ldap_rdn'     : 'login'
			}
		}
	)
	id = Column(
		'uid',
		UInt32(),
		Sequence('users_uid_seq'),
		Comment('User ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID'),
			'ldap_attr'     : 'uidNumber'
		}
	)
	group_id = Column(
		'gid',
		UInt32(),
		ForeignKey('groups.gid', name='users_fk_gid', onupdate='CASCADE'),
		Comment('Group ID'),
		nullable=False,
		info={
			'header_string' : _('Group'),
			'filter_type'   : 'list',
			'ldap_attr'     : 'gidNumber',
			'column_flex'   : 2
		}
	)
	security_policy_id = Column(
		'secpolid',
		UInt32(),
		ForeignKey('secpol_def.secpolid', name='users_fk_secpolid', onupdate='CASCADE'),
		Comment('Security policy ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Security Policy'),
			'column_flex'   : 2
		}
	)
	state = Column(
		UserState.db_type(),
		Comment('User state'),
		nullable=False,
		default=UserState.pending,
		server_default=UserState.pending,
		info={
			'header_string' : _('State'),
			'ldap_attr'     : 'npAccountStatus',
			'ldap_value'    : 'ldap_status'
		}
	)
	login = Column(
		ExactUnicode(48),
		Comment('Login string'),
		nullable=False,
		info={
			'header_string' : _('Username'),
			'writer'        : 'change_login',
			'pass_request'  : True,
			'ldap_attr'     : ('uid', 'xmozillanickname', 'gecos', 'displayName'),
			'column_flex'   : 2
		}
	)
	password = Column(
		'pass',
		ASCIIString(255),
		Comment('Some form of password'),
		nullable=False,
		info={
			'header_string' : _('Password'),
			'secret_value'  : True,
			'editor_xtype'  : 'passwordfield',
			'writer'        : 'change_password',
			'validator'     : _validate_user_password,
			'pass_request'  : True,
			'ldap_attr'     : 'userPassword', # FIXME!
			'ldap_value'    : 'ldap_password'
		}
	)
	a1_hash = Column(
		'a1hash',
		ASCIIFixedString(32),
		Comment('DIGEST-MD5 A1 hash'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('A1 Hash'),
			'secret_value'  : True,
			'editor_xtype'  : None,
			'ldap_attr'     : 'npDigestHA1'
		}
	)
	enabled = Column(
		NPBoolean(),
		Comment('Is logging in enabled?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Enabled')
		}
	)
	name_family = Column(
		Unicode(255),
		Comment('Family name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Family Name'),
			'ldap_attr'     : ('sn', 'cn'), # FIXME: move 'cn' to dynamic attr
			'column_flex'   : 3
		}
	)
	name_given = Column(
		Unicode(255),
		Comment('Given name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Given Name'),
			'ldap_attr'     : 'givenName',
			'column_flex'   : 3
		}
	)
	name_middle = Column(
		Unicode(255),
		Comment('Middle name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Middle Name'),
			'ldap_attr'     : 'initials', # FIXME?
			'column_flex'   : 3
		}
	)
	title = Column(
		Unicode(255),
		Comment('Title'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Title'),
			'ldap_attr'     : 'title'
		}
	)
	manager_id = Column(
		'managerid',
		UInt32(),
		ForeignKey('users.uid', name='users_fk_managerid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Manager user ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Manager'),
			'column_flex'   : 2
		}
	)
	email = Column(
		Unicode(64),
		Comment('User\'s e-mail'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('E-mail'),
			'vtype'         : 'email',
			'ldap_attr'     : 'mail',
			'column_flex'   : 2
		}
	)
	ip_address = Column(
		'ipaddr',
		IPv4Address(),
		Comment('Lock-in IP address'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IP Address')
		}
	)
	random_key = Column(
		'randomkey',
		ASCIIString(64),
		Comment('Activation random key'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Random Key')
		}
	)
	photo_id = Column(
		'photo',
		UInt32(),
		ForeignKey('files_def.fileid', name='users_fk_photo', ondelete='SET NULL', onupdate='CASCADE', use_alter=True),
		Comment('Photo File ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Photo')
		}
	)

	photo = relationship(
		'File',
		backref='photo_of',
		foreign_keys=(photo_id,)
	)
	secondary_groupmap = relationship(
		'UserGroup',
		backref=backref('user', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	dav_locks = relationship(
		'DAVLock',
		backref='user',
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	subordinates = relationship(
		'User',
		backref=backref('manager', remote_side=[id])
	)
	caps = relationship(
		'UserCapability',
		collection_class=attribute_mapped_collection('code'),
		backref=backref('user', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	aclmap = relationship(
		'UserACL',
		collection_class=attribute_mapped_collection('code_res'),
		backref=backref('user', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	files = relationship(
		'File',
		backref='user',
		primaryjoin='File.user_id == User.id'
	)
	folders = relationship(
		'FileFolder',
		backref='user',
		primaryjoin='FileFolder.user_id == User.id'
	)
	password_history = relationship(
		'PasswordHistory',
		backref=backref('user', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	setting_map = relationship(
		'UserSetting',
		collection_class=attribute_mapped_collection('name'),
		backref=backref('user', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	data_cache_map = relationship(
		'DataCache',
		collection_class=attribute_mapped_collection('name'),
		backref=backref('user', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	sessions = relationship(
		'NPSession',
		backref='user',
		passive_deletes=True
	)
	calendars = relationship(
		'Calendar',
		backref=backref('user', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	calendar_imports = relationship(
		'CalendarImport',
		backref=backref('user', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	events = relationship(
		'Event',
		backref=backref('user', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	secondary_groups = association_proxy(
		'secondary_groupmap',
		'group',
		creator=lambda v: UserGroup(group=v)
	)
	privileges = association_proxy(
		'caps',
		'value',
		creator=lambda k,v: _gen_xcap(UserCapability, k, v)
	)
	acls = association_proxy(
		'aclmap',
		'value',
		creator=lambda k,v: _gen_xacl(UserACL, k, v)
	)
	settings = association_proxy(
		'setting_map',
		'python_value',
		creator=_gen_user_setting
	)
	data_cache = association_proxy(
		'data_cache_map',
		'value',
		creator=lambda k,v: DataCache(name=k, value=v)
	)

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		self.vcard = None
		self.mod_pw = False

	def __str__(self):
		return '%s' % str(self.login)

	@hybrid_property
	def name_full(self):
		return self.name_family + ' ' + self.name_given

	def generate_salt(self, salt_len=4, system_rng=True, chars=(string.ascii_lowercase + string.ascii_uppercase + string.digits)):
		if system_rng:
			try:
				rng = random.SystemRandom()
			except NotImplementedError:
				rng = random
		else:
			rng = random
		return ''.join(rng.choice(chars) for i in range(salt_len))

	def ldap_status(self, settings):
		if self.state == UserState.pending:
			return 'noaccess'
		elif self.state == UserState.active:
			if self.enabled:
				return 'active'
			else:
				return 'disabled'
		else:
			return 'deleted'

	def ldap_password(self, settings):
		pw = getattr(self, 'mod_pw', False)
		if not pw:
			raise ValueError('Temporary plaintext password was not found')
		salt = self.generate_salt(4).encode()
		ctx = hashlib.sha1()
		ctx.update(pw.encode())
		ctx.update(salt)
		return '{SSHA}' + base64.b64encode(ctx.digest() + salt).decode()

	def generate_a1hash(self, realm):
		ctx = hashlib.md5()
		ctx.update(('%s:%s:%s' % (self.login, realm, self.mod_pw)).encode())
		return ctx.hexdigest()

	def check_password(self, pwd, hash_con='sha1', salt_len=4):
		if isinstance(pwd, str):
			pwd = pwd.encode()
		salt = self.password[:salt_len].encode()
		orig = self.password[salt_len:]
		ctx = hashlib.new(hash_con)
		ctx.update(salt)
		ctx.update(pwd)
		return ctx.hexdigest() == orig

	def change_login(self, newlogin, opts, request):
		reg = request.registry
		self.login = newlogin
		if getattr(self, 'mod_pw', False):
			realm = reg.settings.get('netprofile.auth.digest_realm', 'NetProfile UI')
			self.a1_hash = self.generate_a1hash(realm)

	def change_password(self, newpwd, opts, request):
		self.mod_pw = newpwd
		ts = dt.datetime.now()
		secpol = self.effective_policy
		if secpol:
			checkpw = secpol.check_new_password(request, self, newpwd, ts)
			if checkpw is not True:
				# FIXME: error reporting
				raise ValueError(checkpw)
		reg = request.registry
		hash_con = reg.settings.get('netprofile.auth.hash', 'sha1')
		salt_len = int(reg.settings.get('netprofile.auth.salt_length', 4))
		salt = self.generate_salt(salt_len)
		ctx = hashlib.new(hash_con)
		ctx.update(salt.encode())
		ctx.update(newpwd.encode())
		newhash = ctx.hexdigest()
		self.password = salt + newhash
		if self.login:
			realm = reg.settings.get('netprofile.auth.digest_realm', 'NetProfile UI')
			self.a1_hash = self.generate_a1hash(realm)
		if secpol:
			secpol.after_new_password(request, self, newpwd, ts)
		if request.user == self:
			request.session['sess.nextcheck'] = ts
			request.session['sess.pwage'] = 'ok'
			if 'sess.pwdays' in request.session:
				del request.session['sess.pwdays']

	@property
	def last_password_change(self):
		return DBSession().query(PasswordHistory)\
			.filter(PasswordHistory.user == self)\
			.order_by(PasswordHistory.timestamp.desc())\
			.first()

	@property
	def sess_timeout(self):
		secpol = self.effective_policy
		if not secpol:
			return None
		sto = secpol.sess_timeout
		if (not sto) or (sto < 30):
			return None
		return sto

	@property
	def flat_privileges(self):
		gpriv = self.group.flat_privileges
		for sg in self.secondary_groups:
			if sg == self.group:
				continue
			gpriv.update(sg.flat_privileges)
		gpriv.update(self.privileges)
		return gpriv

	@property
	def group_names(self):
		names = []
		if self.group:
			names.append(self.group.name)
		for sg in self.secondary_groups:
			if sg == self.group:
				continue
			names.append(sg.name)
		return names

	@property
	def effective_policy(self):
		if self.security_policy:
			return self.security_policy
		grp = self.group
		secpol = None
		while grp and (secpol is None):
			secpol = grp.security_policy
			grp = grp.parent
		return secpol

	def client_settings(self, req):
		sess = DBSession()
		ret = {}
		for ust in sess.query(UserSettingType):
			if not ust.client_ok:
				continue
			if ust.name in self.settings:
				ret[ust.name] = self.settings[ust.name]
			else:
				ret[ust.name] = ust.parse_param(ust.default)
		return ret

	def client_acls(self, req):
		ret = {}
		for priv, res in self.acls:
			if priv not in ret:
				ret[priv] = {}
			ret[priv][res] = self.acls[(priv, res)]
		return ret

	def generate_session(self, req, sname, now=None):
		if now is None:
			now = dt.datetime.now()
		npsess = NPSession(
			user=self,
			login=self.login,
			session_name=sname,
			start_time=now,
			last_time=now
		)
		if req.remote_addr is not None:
			try:
				ip = ipaddr.IPAddress(req.remote_addr)
				if isinstance(ip, ipaddr.IPv4Address):
					npsess.ip_address = ip
				elif isinstance(ip, ipaddr.IPv6Address):
					npsess.ipv6_address = ip
			except ValueError:
				pass
		secpol = self.effective_policy
		if secpol and (not secpol.check_new_session(req, self, npsess, now)):
			return None
		return npsess

	def group_vector(self):
		vec = [ self.group_id ]
		for sg in self.secondary_groups:
			vec.append(sg.id)
		return vec

	def is_member_of(self, grp):
		if self == grp:
			return True
		if not isinstance(grp, Group):
			return False
		xgrp = self.group
		while xgrp:
			if xgrp == grp:
				return True
			xgrp = xgrp.parent
		for xgrp in self.secondary_groups:
			if xgrp == grp:
				return True
		return False

	def get_root_folder(self):
		if self.group is None:
			return None
		ff = self.group.effective_root_folder
		if ff is None:
			root_uid = global_setting('vfs_root_uid')
			root_gid = global_setting('vfs_root_gid')
			root_rights = global_setting('vfs_root_rights')
			allow_read = False
			allow_write = False
			allow_traverse = False
			if self.id == root_uid:
				allow_read = bool(root_rights & F_OWNER_READ)
				allow_write = bool(root_rights & F_OWNER_WRITE)
				allow_traverse = bool(root_rights & F_OWNER_EXEC)
			elif root_gid in self.group_vector():
				allow_read = bool(root_rights & F_GROUP_READ)
				allow_write = bool(root_rights & F_GROUP_WRITE)
				allow_traverse = bool(root_rights & F_GROUP_EXEC)
			else:
				allow_read = bool(root_rights & F_OTHER_READ)
				allow_write = bool(root_rights & F_OTHER_WRITE)
				allow_traverse = bool(root_rights & F_OTHER_EXEC)
			return {
				'id'             : 'root',
				'name'           : 'root',
				'allow_read'     : allow_read,
				'allow_write'    : allow_write,
				'allow_traverse' : allow_traverse,
				'parent_write'   : (allow_traverse and allow_write)
			}
		p_wr = False
		if ff.parent:
			p_wr = ff.parent.can_write(self)
		else:
			root_uid = global_setting('vfs_root_uid')
			root_gid = global_setting('vfs_root_gid')
			root_rights = global_setting('vfs_root_rights')
			if self.id == root_uid:
				p_wr = bool(root_rights & F_OWNER_WRITE)
			elif root_gid in self.group_vector():
				p_wr = bool(root_rights & F_GROUP_WRITE)
			else:
				p_wr = bool(root_rights & F_OTHER_WRITE)
		return {
			'id'             : ff.id,
			'name'           : ff.name,
			'allow_read'     : ff.can_read(self),
			'allow_write'    : ff.can_write(self),
			'allow_traverse' : ff.can_traverse_path(self),
			'parent_write'   : p_wr
		}

	@property
	def root_readable(self):
		ff = self.group.effective_root_folder
		if ff is not None:
			return ff.can_read(self)
		root_uid = global_setting('vfs_root_uid')
		root_gid = global_setting('vfs_root_gid')
		root_rights = global_setting('vfs_root_rights')
		if self.id == root_uid:
			return bool(root_rights & F_OWNER_READ)
		if root_gid in self.group_vector():
			return bool(root_rights & F_GROUP_READ)
		return bool(root_rights & F_OTHER_READ)

	@property
	def root_writable(self):
		ff = self.group.effective_root_folder
		if ff is not None:
			return ff.can_write(self)
		root_uid = global_setting('vfs_root_uid')
		root_gid = global_setting('vfs_root_gid')
		root_rights = global_setting('vfs_root_rights')
		if self.id == root_uid:
			return bool(root_rights & F_OWNER_WRITE)
		if root_gid in self.group_vector():
			return bool(root_rights & F_GROUP_WRITE)
		return bool(root_rights & F_OTHER_WRITE)

	@property
	def __name__(self):
		return self.login

	def ldap_attrs(self, settings):
		from netprofile_ldap.ldap import get_dn
		groupset = set()
		if self.group:
			groupset.add(self.group)
		for g in self.secondary_groups:
			groupset.add(g)
		dnlist = []
		for g in groupset:
			dnlist.append(get_dn(g, settings))
		ret = {}
		if self.login:
			ret['homeDirectory'] = '/home/%s' % (self.login,)
		if 'netprofile.ldap.orm.User.default_shell' in settings:
			ret['loginShell'] = settings['netprofile.ldap.orm.User.default_shell']
		if len(dnlist) > 0:
			ret['memberOf'] = dnlist
		return ret

	def get_uri(self):
		return [ '', 'users', self.login ]

	def dav_props(self, pset):
		vcard = getattr(self, 'vcard', None)
		if vcard is None:
			self.vcard = self._get_vcard()

		ret = {}
		if dprops.RESOURCE_TYPE in pset:
			ret[dprops.RESOURCE_TYPE] = DAVResourceTypeValue(dprops.PRINCIPAL)
		if dprops.CONTENT_LENGTH in pset:
			ret[dprops.CONTENT_LENGTH] = self.vcard.content_length
		if dprops.CONTENT_TYPE in pset:
			ret[dprops.CONTENT_TYPE] = 'text/x-vcard'
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = self.login
		if dprops.ETAG in pset:
			ret[dprops.ETAG] = '"%s"' % self.vcard.etag
		return ret

	def dav_group_members(self, req):
		return set()

	def dav_memberships(self, req):
		gmset = set()
		if self.group:
			gmset.add(self.group)
		gmset.update(self.secondary_groups)
		return gmset

	def dav_alt_uri(self, req):
		uris = []
		if self.email:
			uris.append('mailto:' + self.email)
		return uris

	def _get_vcard(self):
		card = cal.Card()
		card.add('VERSION', '3.0')

		fname = []
		if self.name_family:
			fname.append(self.name_family)
		if self.name_given:
			fname.append(self.name_given)
		if self.name_middle:
			fname.append(self.name_middle)
		if len(fname) == 0:
			fname = (self.login,)
		if self.id:
			card.add('UID', icalendar.vUri('urn:npobj:user:%s:%u' % (
				inst_id,
				self.id
			)))
		card.add('N', cal.vStructuredUnicode(*fname))
		card.add('FN', cal.vUnicode(' '.join(fname)))
		card.add('NICKNAME', cal.vUnicode(self.login))
		if self.email:
			card.add('EMAIL', cal.vEMail(self.email))

		ical = card.to_ical()
		resp = Response(ical, content_type='text/x-vcard', charset='utf-8')
		if PY3:
			resp.content_disposition = \
				'attachment; filename*=UTF-8\'\'%s.vcf' % (
					urllib.parse.quote(self.login, '')
				)
		else:
			resp.content_disposition = \
				'attachment; filename*=UTF-8\'\'%s.vcf' % (
					urllib.quote(self.login.encode(), '')
				)
		ctx = hashlib.md5()
		ctx.update(ical)
		resp.etag = ctx.hexdigest()
		return resp

	def dav_get(self, req):
		vcard = getattr(self, 'vcard', None)
		if vcard is None:
			self.vcard = self._get_vcard()
		return self.vcard

	@validates('name_family', 'name_given', 'name_middle', 'login', 'email')
	def _reset_vcard(self, k, v):
		self.vcard = None
		return v

	@classmethod
	def get_acls(cls):
		sess = DBSession()
		res = {}
		for u in sess.query(User):
			res[u.id] = str(u)
		return res

def _del_user(mapper, conn, tgt):
	sess = DBSession()
	sess.query(UserACL)\
		.filter(
			UserACL.privilege_id.in_(sess.query(Privilege.id).filter(Privilege.resource_class == 'NPUser')),
			UserACL.resource == tgt.id
		)\
		.delete(synchronize_session=False)

event.listen(User, 'after_delete', _del_user)

@implementer(IDAVFile, IDAVPrincipal)
class Group(Base):
	"""
	Defines a group of NetProfile users.
	"""
	__tablename__ = 'groups'
	__table_args__ = (
		Comment('Groups'),
		Index('groups_u_name', 'name', unique=True),
		Index('groups_i_parentid', 'parentid'),
		Index('groups_i_secpolid', 'secpolid'),
		Index('groups_i_rootffid', 'rootffid'),
		Trigger('after', 'insert', 't_groups_ai'),
		Trigger('after', 'update', 't_groups_au'),
		Trigger('after', 'delete', 't_groups_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_GROUPS',
				'cap_read'     : 'GROUPS_LIST',
				'cap_create'   : 'GROUPS_CREATE',
				'cap_edit'     : 'GROUPS_EDIT',
				'cap_delete'   : 'GROUPS_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : _('Groups'),
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('gid', 'name', 'parent', 'security_policy', 'root_folder'),
				'grid_hidden'  : ('gid',),
				'form_view'    : ('name', 'parent', 'security_policy', 'visible', 'assignable', 'root_folder'),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' :
					Wizard(
						Step('name', 'parent', 'security_policy', title=_('New group data')),
						Step('visible', 'assignable', 'root_folder', title=_('New group details')),
						title=_('Add new group')
					),

				'ldap_classes' : ('npGroup',),
				'ldap_rdn'     : 'name'
			}
		}
	)
	id = Column(
		'gid',
		UInt32(),
		Sequence('groups_gid_seq'),
		Comment('Group ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID'),
			'ldap_attr'     : 'gidNumber'
		}
	)
	parent_id = Column(
		'parentid',
		UInt32(),
		ForeignKey('groups.gid', name='groups_fk_parentid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Parent group ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Parent'),
			'filter_type'   : 'list',
			'column_flex'   : 3
		}
	)
	security_policy_id = Column(
		'secpolid',
		UInt32(),
		ForeignKey('secpol_def.secpolid', name='groups_fk_secpolid', onupdate='CASCADE'),
		Comment('Security policy ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Security Policy'),
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	name = Column(
		Unicode(255),
		Comment('Group name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'ldap_attr'     : 'cn',
			'column_flex'   : 3
		}
	)
	visible = Column(
		NPBoolean(),
		Comment('Is visible in UI?'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : _('Visible')
		}
	)
	assignable = Column(
		NPBoolean(),
		Comment('Can be assigned tasks?'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : _('Assignable')
		}
	)
	root_folder_id = Column(
		'rootffid',
		UInt32(),
		ForeignKey('files_folders.ffid', name='groups_fk_rootffid', ondelete='SET NULL', onupdate='CASCADE', use_alter=True),
		Comment('Root file folder ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Root Folder'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	secondary_usermap = relationship(
		'UserGroup',
		backref=backref('group', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	users = relationship(
		'User',
		backref=backref('group', innerjoin=True)
	)
	children = relationship(
		'Group',
		backref=backref('parent', remote_side=[id])
	)
	caps = relationship(
		'GroupCapability',
		collection_class=attribute_mapped_collection('privilege.code'),
		backref=backref('group', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	aclmap = relationship(
		'GroupACL',
		collection_class=attribute_mapped_collection('code_res'),
		backref=backref('group', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	files = relationship(
		'File',
		backref='group',
		primaryjoin='File.group_id == Group.id'
	)
	folders = relationship(
		'FileFolder',
		backref='group',
		primaryjoin='FileFolder.group_id == Group.id'
	)
	calendars = relationship(
		'Calendar',
		backref=backref('group', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	secondary_users = association_proxy(
		'secondary_usermap',
		'user'
	)
	privileges = association_proxy(
		'caps',
		'value',
		creator=lambda k,v: _gen_xcap(GroupCapability, k, v)
	)
	acls = association_proxy(
		'aclmap',
		'value',
		creator=lambda k,v: _gen_xacl(GroupACL, k, v)
	)

	def __str__(self):
		return '%s' % str(self.name)

	@property
	def flat_privileges(self):
		ppriv = {}
		if self.parent is None:
			return self.privileges.copy()
		ppriv = self.parent.flat_privileges
		ppriv.update(self.privileges)
		return ppriv

	@property
	def effective_policy(self):
		if self.security_policy:
			return self.security_policy
		grp = self.parent
		secpol = None
		while grp and (secpol is None):
			secpol = grp.security_policy
			grp = grp.parent
		return secpol

	@property
	def effective_root_folder(self):
		if self.root_folder:
			return self.root_folder
		grp = self.parent
		ff = None
		while grp and (ff is None):
			ff = grp.root_folder
			grp = grp.parent
		return ff

	@property
	def __name__(self):
		return self.name

	def ldap_attrs(self, settings):
		from netprofile_ldap.ldap import get_dn
		userset = set()
		for u in self.users:
			userset.add(u)
		for u in self.secondary_users:
			userset.add(u)
		dnlist = []
		for u in userset:
			dnlist.append(get_dn(u, settings))
		ret = {}
		if len(dnlist) > 0:
			ret['uniqueMember'] = dnlist
		return ret

	def get_uri(self):
		return [ '', 'groups', self.name ]

	def dav_props(self, pset):
		ret = {}
		if dprops.RESOURCE_TYPE in pset:
			ret[dprops.RESOURCE_TYPE] = DAVResourceTypeValue(dprops.PRINCIPAL)
		if dprops.CONTENT_TYPE in pset:
			ret[dprops.CONTENT_TYPE] = 'text/x-vcard'
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = self.name
		return ret

	def dav_group_members(self, req):
		gmset = set()
		gmset.update(self.children)
		gmset.update(self.users)
		gmset.update(self.secondary_users)
		return gmset

	def dav_memberships(self, req):
		gmset = set()
		if self.parent:
			gmset.add(self.parent)
		return gmset

	def is_member_of(self, grp):
		if not isinstance(grp, Group):
			return False
		xgrp = self
		while xgrp:
			if xgrp == grp:
				return True
			xgrp = xgrp.parent
		return False

	@classmethod
	def get_acls(cls):
		sess = DBSession()
		res = {}
		for g in sess.query(Group):
			res[g.id] = str(g)
		return res

def _del_group(mapper, conn, tgt):
	sess = DBSession()
	sess.query(GroupACL)\
		.filter(
			GroupACL.privilege_id.in_(sess.query(Privilege.id).filter(Privilege.resource_class == 'NPGroup')),
			GroupACL.resource == tgt.id
		)\
		.delete(synchronize_session=False)

event.listen(Group, 'after_delete', _del_group)

class Privilege(Base):
	"""
	Generic privilege code, to be assigned to users or groups.
	"""
	__tablename__ = 'privileges'
	__table_args__ = (
		Comment('Privilege definitions'),
		Index('privileges_u_code', 'code', unique=True),
		Index('privileges_u_name', 'name', unique=True),
		Index('privileges_i_canbeset', 'canbeset'),
		Index('privileges_i_npmodid', 'npmodid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'PRIVILEGES_LIST',
				'cap_create'   : 'PRIVILEGES_CREATE',
				'cap_edit'     : 'PRIVILEGES_EDIT',
				'cap_delete'   : 'PRIVILEGES_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : _('Privileges'),
				'default_sort' : ({ 'property': 'code' ,'direction': 'ASC' },),
				'grid_view'    : ('privid', 'module', 'code', 'name', 'guestvalue', 'hasacls', 'canbeset'),
				'grid_hidden'  : ('privid', 'canbeset'),
				'form_view'    : ('module', 'code', 'name', 'guestvalue', 'hasacls', 'resclass'),
				'easy_search'  : ('code', 'name'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple'),

				# FIXME: temporary wizard
				'create_wizard' : SimpleWizard(title=_('Add new privilege'))
			}
		}
	)
	id = Column(
		'privid',
		UInt32(),
		Sequence('privileges_privid_seq'),
		Comment('Privilege ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	module_id = Column(
		'npmodid',
		UInt32(),
		ForeignKey('np_modules.npmodid', name='privileges_fk_npmodid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('NetProfile module ID'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('Module'),
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	can_be_set = Column(
		'canbeset',
		NPBoolean(),
		Comment('Can be set from UI?'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : _('Can be Set')
		}
	)
	code = Column(
		ASCIIString(48),
		Comment('Privilege code'),
		nullable=False,
		info={
			'header_string' : _('Code'),
			'column_flex'   : 2
		}
	)
	name = Column(
		Unicode(255),
		Comment('Privilege name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	guest_value = Column(
		'guestvalue',
		NPBoolean(),
		Comment('Value for users not logged in'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Guest Value')
		}
	)
	has_acls = Column(
		'hasacls',
		NPBoolean(),
		Comment('Can have ACLs?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Has ACLs')
		}
	)
	resource_class = Column(
		'resclass',
		ASCIIString(255),
		Comment('Resource provider class'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Resource Class')
		}
	)
	group_caps = relationship(
		'GroupCapability',
		backref=backref('privilege', lazy='subquery', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	user_caps = relationship(
		'UserCapability',
		backref=backref('privilege', lazy='subquery', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	group_acls = relationship(
		'GroupACL',
		backref=backref('privilege', lazy='subquery', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	user_acls = relationship(
		'UserACL',
		backref=backref('privilege', lazy='subquery', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		return '%s' % str(self.code)

	def get_acls(self):
		if (not self.has_acls) or (not self.resource_class):
			return None
		cls = self.resource_class
		if cls[:2] == 'NP':
			cls = cls[2:]
		if cls not in Base._decl_class_registry:
			return None
		cls = Base._decl_class_registry[cls]
		getter = getattr(cls, 'get_acls', None)
		if callable(getter):
			return getter()

class Capability(object):
	"""
	Abstract prototype for privilege assignment object.
	"""
	@declared_attr
	def id(cls):
		return Column(
			'capid',
			UInt32(),
			Sequence('capid_seq'), # FIXME: needs different names
			Comment('Capability ID'),
			primary_key=True,
			nullable=False,
			info={
				'header_string' : _('ID')
			}
		)

	@declared_attr
	def privilege_id(cls):
		return Column(
			'privid',
			UInt32(),
			ForeignKey('privileges.privid', name=(cls.__tablename__ + '_fk_privid'), ondelete='CASCADE', onupdate='CASCADE'),
			Comment('Privilege ID'),
			nullable=False,
			info={
				'header_string' : _('Privilege')
			}
		)

	@declared_attr
	def value(cls):
		return Column(
			NPBoolean(),
			Comment('Capability value'),
			nullable=False,
			default=True,
			server_default=npbool(True),
			info={
				'header_string' : _('Value')
			}
		)

	def __str__(self):
		return '<%s(%s) = %s>' % (
			str(self.__class__.__name__),
			str(self.code),
			str(self.value)
		)

	@property
	def code(self):
		return self.privilege.code

class GroupCapability(Capability,Base):
	"""
	Group privilege assignment object.
	"""
	__tablename__ = 'capabilities_groups'
	__table_args__ = (
		Comment('Group capabilities'),
		Index('capabilities_groups_u_cap', 'gid', 'privid', unique=True),
		Index('capabilities_groups_i_priv', 'privid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_read'     : 'GROUPS_GETCAP',
				'cap_create'   : 'GROUPS_SETCAP',
				'cap_edit'     : 'GROUPS_SETCAP',
				'cap_delete'   : 'GROUPS_SETCAP',

#				'show_in_menu' : 'admin',
				'menu_name'    : _('Group Capabilities'),
				'default_sort' : (),
#				'grid_view'    : ('code', 'name', 'guestvalue', 'hasacls')
			}
		}
	)
	group_id = Column(
		'gid',
		UInt32(),
		ForeignKey('groups.gid', name='capabilities_groups_fk_gid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Group ID'),
		nullable=False,
		info={
			'header_string' : _('Group')
		}
	)

class UserCapability(Capability,Base):
	"""
	User privilege assignment object.
	"""
	__tablename__ = 'capabilities_users'
	__table_args__ = (
		Comment('User capabilities'),
		Index('capabilities_users_u_cap', 'uid', 'privid', unique=True),
		Index('capabilities_users_i_priv', 'privid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_read'     : 'USERS_GETCAP',
				'cap_create'   : 'USERS_SETCAP',
				'cap_edit'     : 'USERS_SETCAP',
				'cap_delete'   : 'USERS_SETCAP',

#				'show_in_menu' : 'admin',
				'menu_name'    : _('User Capabilities'),
				'default_sort' : (),
#				'grid_view'    : ('code', 'name', 'guestvalue', 'hasacls')
			}
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='capabilities_users_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : _('User')
		}
	)

class ACL(object):
	"""
	Abstract prototype for resource-specific privilege assignment object.
	"""
	@declared_attr
	def id(cls):
		return Column(
			'aclid',
			UInt32(),
			Sequence('aclid_seq'), # FIXME: needs different names
			Comment('ACL ID'),
			primary_key=True,
			nullable=False,
			info={
				'header_string' : _('ID')
			}
		)

	@declared_attr
	def privilege_id(cls):
		return Column(
			'privid',
			UInt32(),
			ForeignKey('privileges.privid', name=(cls.__tablename__ + '_fk_privid'), ondelete='CASCADE', onupdate='CASCADE'),
			Comment('Privilege ID'),
			nullable=False,
			info={
				'header_string' : _('Privilege')
			}
		)

	@declared_attr
	def resource(cls):
		return Column(
			UInt32(),
			Comment('Resource ID'),
			nullable=False,
			info={
				'header_string' : _('Resource')
			}
		)

	@declared_attr
	def value(cls):
		return Column(
			NPBoolean(),
			Comment('Access value'),
			nullable=False,
			default=True,
			server_default=npbool(True),
			info={
				'header_string' : _('Value')
			}
		)

	def __str__(self):
		return '<%s(%s,%u) = %s>' % (
			str(self.__class__.__name__),
			str(self.code),
			str(self.resource),
			str(self.value)
		)

	@property
	def code(self):
		return self.privilege.code

	@property
	def code_res(self):
		return self.code, self.resource

class GroupACL(ACL,Base):
	"""
	Group resource-specific privilege assignment object.
	"""
	__tablename__ = 'acls_groups'
	__table_args__ = (
		Comment('Group access control lists'),
		Index('acls_groups_u_cap', 'gid', 'privid', 'resource', unique=True),
		Index('acls_groups_i_priv', 'privid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
			}
		}
	)
	group_id = Column(
		'gid',
		UInt32(),
		ForeignKey('groups.gid', name='acls_groups_fk_gid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Group ID'),
		nullable=False,
		info={
			'header_string' : _('Group')
		}
	)

class UserACL(ACL,Base):
	"""
	User resource-specific privilege assignment object.
	"""
	__tablename__ = 'acls_users'
	__table_args__ = (
		Comment('User access control lists'),
		Index('acls_users_u_cap', 'uid', 'privid', 'resource', unique=True),
		Index('acls_users_i_priv', 'privid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
			}
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='acls_users_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : _('User')
		}
	)

class UserGroup(Base):
	"""
	Secondary group membership association object.
	"""
	__tablename__ = 'users_groups'
	__table_args__ = (
		Comment('Secondary user groups'),
		Index('users_groups_u_mapping', 'uid', 'gid', unique=True),
		Index('users_groups_i_gid', 'gid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
			}
		}
	)
	id = Column(
		'ugid',
		UInt32(),
		Sequence('users_groups_ugid_seq'),
		Comment('User group mapping ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='users_groups_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : _('User')
		}
	)
	group_id = Column(
		'gid',
		UInt32(),
		ForeignKey('groups.gid', name='users_groups_fk_gid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Group ID'),
		nullable=False,
		info={
			'header_string' : _('Group')
		}
	)

	def __str__(self):
		return '%s' % str(self.group)

class SecurityPolicyOnExpire(DeclEnum):
	"""
	On-password-expire security policy action.
	"""
	none  = 'none',  _('No action'),          10
	force = 'force', _('Force new password'), 20
	drop  = 'drop',  _('Drop connection'),    30

class SecurityPolicy(Base):
	"""
	Assignable security policy for users and groups.
	"""
	__tablename__ = 'secpol_def'
	__table_args__ = (
		Comment('Security policies'),
		Index('secpol_def_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'SECPOL_LIST',
				'cap_create'   : 'SECPOL_CREATE',
				'cap_edit'     : 'SECPOL_EDIT',
				'cap_delete'   : 'SECPOL_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : _('Security Policies'),
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('secpolid', 'name', 'pw_length_min', 'pw_length_max', 'pw_ctype_min', 'pw_ctype_max', 'pw_dict_check', 'pw_hist_check', 'pw_hist_size', 'sess_timeout'),
				'grid_hidden'  : ('secpolid', 'sess_timeout'),
				'form_view'    : (
					'name', 'descr',
					'pw_length_min', 'pw_length_max',
					'pw_ctype_min', 'pw_ctype_max',
					'pw_dict_check', 'pw_dict_name',
					'pw_hist_check', 'pw_hist_size',
					'pw_age_min', 'pw_age_max', 'pw_age_warndays', 'pw_age_warnmail', 'pw_age_action',
					'net_whitelist', 'sess_timeout',
					'sess_window_ipv4', 'sess_window_ipv6'
				),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'secpolid',
		UInt32(),
		Sequence('secpol_def_secpolid_seq'),
		Comment('Security policy ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Security policy name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	pw_length_min = Column(
		UInt16(),
		Comment('Minimum password length'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Min. Password Len.')
		}
	)
	pw_length_max = Column(
		UInt16(),
		Comment('Maximum password length'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Max. Password Len.')
		}
	)
	pw_ctype_min = Column(
		UInt8(),
		Comment('Minimum number of character types in password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Min. Char Types')
		}
	)
	pw_ctype_max = Column(
		UInt8(),
		Comment('Maximum number of character types in password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Max. Char Types')
		}
	)
	pw_dict_check = Column(
		NPBoolean(),
		Comment('Check password against a dictionary?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Dictionary Check')
		}
	)
	pw_dict_name = Column(
		ASCIIString(255),
		Comment('Name of a custom dictionary'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Custom Dictionary')
		}
	)
	pw_hist_check = Column(
		NPBoolean(),
		Comment('Keep a history of old passwords?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Keep History')
		}
	)
	pw_hist_size = Column(
		UInt16(),
		Comment('Old password history size'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('History Size')
		}
	)
	pw_age_min = Column(
		UInt16(),
		Comment('Minimum password age in days'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Min. Password Age')
		}
	)
	pw_age_max = Column(
		UInt16(),
		Comment('Maximum password age in days'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Max. Password Age')
		}
	)
	pw_age_warndays = Column(
		UInt16(),
		Comment('Notify to change password (in days before expiration)'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Notify Days')
		}
	)
	pw_age_warnmail = Column(
		NPBoolean(),
		Comment('Warn about password expiry by e-mail'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Warn by E-mail')
		}
	)
	pw_age_action = Column(
		SecurityPolicyOnExpire.db_type(),
		Comment('Action on expired password'),
		nullable=False,
		default=SecurityPolicyOnExpire.none,
		server_default=SecurityPolicyOnExpire.none,
		info={
			'header_string' : _('On Expire')
		}
	)
	net_whitelist = Column(
		ASCIIString(255),
		Comment('Whitelist of allowed login addresses'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Address Whitelist')
		}
	)
	sess_timeout = Column(
		UInt32(),
		Comment('Session timeout (in seconds)'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Session Timeout')
		}
	)
	sess_window_ipv4 = Column(
		UInt8(),
		Comment('Allow IPv4 source addresses to migrate within this mask'),
		nullable=True,
		default=32,
		server_default=text('32'),
		info={
			'header_string' : _('IPv4 Session Window')
		}
	)
	sess_window_ipv6 = Column(
		UInt8(),
		Comment('Allow IPv6 source addresses to migrate within this mask'),
		nullable=True,
		default=128,
		server_default=text('128'),
		info={
			'header_string' : _('IPv6 Session Window')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Security policy description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)
	users = relationship(
		'User',
		backref='security_policy'
	)
	groups = relationship(
		'Group',
		backref='security_policy'
	)

	@property
	def net_whitelist_acl(self):
		if not self.net_whitelist:
			return None
		nets = []
		for ace in self.net_whitelist.split(';'):
			try:
				nets.append(ipaddr.IPNetwork(ace.strip()))
			except ValueError:
				pass
		return nets

	def check_new_password(self, req, user, pwd, ts):
		err = []
		if self.pw_length_min and (len(pwd) < self.pw_length_min):
			err.append('pw_length_min')
		if self.pw_length_max and (len(pwd) > self.pw_length_max):
			err.append('pw_length_max')
		if self.pw_ctype_min or self.pw_ctype_max:
			has_lower = False
			has_upper = False
			has_digit = False
			has_space = False
			has_sym = False
			for char in pwd:
				if char.islower():
					has_lower = True
				elif char.isupper():
					has_upper = True
				elif char.isdigit():
					has_digit = True
				elif char.isspace():
					has_space = True
				elif char.isprintable():
					has_sym = True
			ct_count = 0
			for ctype in (has_lower, has_upper, has_digit, has_space, has_sym):
				if ctype:
					ct_count += 1
			if self.pw_ctype_min and (ct_count < self.pw_ctype_min):
				err.append('pw_ctype_min')
			if self.pw_ctype_max and (ct_count > self.pw_ctype_max):
				err.append('pw_ctype_max')
		if self.pw_dict_check:
			if self.pw_dict_name:
				dname = self.pw_dict_name
			else:
				dname = _DEFAULT_DICT
			dname = dname.split(':')
			if len(dname) == 2:
				from cracklib import FascistCheck
				from pkg_resources import resource_filename
				dfile = resource_filename(dname[0], dname[1])
				try:
					FascistCheck(pwd, dfile)
				except ValueError:
					err.append('pw_dict_check')
		if user and user.id:
			if req and self.pw_hist_check:
				hist_salt = req.registry.settings.get('netprofile.pwhistory_salt', 'nppwdhist_')
				ctx = hashlib.sha1()
				ctx.update(hist_salt.encode())
				ctx.update(pwd.encode())
				hist_hash = ctx.hexdigest()
				for pwh in user.password_history:
					if pwh.password == hist_hash:
						err.append('pw_hist_check')
			if self.pw_age_min:
				delta = dt.timedelta(self.pw_age_min)
				minage_fail = False
				for pwh in user.password_history:
					if (pwh.timestamp + delta) > ts:
						minage_fail = True
				if minage_fail:
					err.append('pw_age_min')
		if len(err) == 0:
			return True
		return err

	def after_new_password(self, req, user, pwd, ts):
		if self.pw_hist_check:
			hist_salt = req.registry.settings.get('netprofile.pwhistory_salt', 'nppwdhist_')
			ctx = hashlib.sha1()
			ctx.update(hist_salt.encode())
			ctx.update(pwd.encode())
			hist_hash = ctx.hexdigest()
			hist_sz = self.pw_hist_size
			if not hist_sz:
				hist_sz = 3
			hist_cursz = len(user.password_history)
			if hist_cursz == hist_sz:
				oldest_time = None
				oldest_idx = None
				for i in range(hist_cursz):
					pwh = user.password_history[i]
					if (oldest_time is None) or (oldest_time > pwh.timestamp):
						oldest_time = pwh.timestamp
						oldest_idx = i
				if oldest_idx is not None:
					del user.password_history[oldest_idx]
			user.password_history.append(PasswordHistory(
				password=hist_hash,
				timestamp=ts
			))

	def check_new_session(self, req, user, npsess, ts=None):
		if ts is None:
			ts = dt.datetime.now()
		addr = npsess.ip_address or npsess.ipv6_address
		acl = self.net_whitelist_acl
		if addr and acl:
			for net in acl:
				if addr in net:
					break
			else:
				return False
		# Expensive checks
		if not self.check_password_age(req, user, npsess, ts):
			return False
		req.session['sess.nextcheck'] = _sess_nextcheck(req, ts)
		return True

	def check_old_session(self, req, user, npsess, ts=None):
		if ts is None:
			ts = dt.datetime.now()
		if self.sess_timeout and npsess.last_time and (self.sess_timeout >= 30):
			delta = ts - npsess.last_time
			if delta.total_seconds() > self.sess_timeout:
				return False
		addr = npsess.ip_address or npsess.ipv6_address
		if req.remote_addr is not None:
			try:
				remote_addr = ipaddr.IPAddress(req.remote_addr)
			except ValueError:
				return False
			if isinstance(remote_addr, ipaddr.IPv4Address) and self.sess_window_ipv4:
				if not isinstance(addr, ipaddr.IPv4Address):
					return False
				try:
					window = ipaddr.IPv4Network('%s/%d' % (str(addr), self.sess_window_ipv4))
				except ValueError:
					return False
				if remote_addr not in window:
					return False
			elif isinstance(remote_addr, ipaddr.IPv6Address) and self.sess_window_ipv6:
				if not isinstance(addr, ipaddr.IPv6Address):
					return False
				try:
					window = ipaddr.IPv6Network('%s/%d' % (str(addr), self.sess_window_ipv6))
				except ValueError:
					return False
				if remote_addr not in window:
					return False
		acl = self.net_whitelist_acl
		if addr and acl:
			for net in acl:
				if addr in net:
					break
			else:
				return False
		if 'sess.nextcheck' in req.session:
			nextcheck = req.session['sess.nextcheck']
		else:
			nextcheck = req.session['sess.nextcheck'] = _sess_nextcheck(req, ts)
		if nextcheck < ts:
			# Expensive checks
			if not self.check_password_age(req, user, npsess, ts):
				return False
			req.session['sess.nextcheck'] = _sess_nextcheck(req, ts)
		return True

	def check_password_age(self, req, user, npsess, ts):
		last_pwh = user.last_password_change
		if last_pwh:
			days = (ts - last_pwh.timestamp).days
			if days > self.pw_age_max:
				if self.pw_age_action == SecurityPolicyOnExpire.drop:
					return False
				req.session['sess.pwage'] = 'force'
			elif self.pw_age_warndays:
				days_left = self.pw_age_max - days
				if days_left < self.pw_age_warndays:
					req.session['sess.pwage'] = 'warn'
					req.session['sess.pwdays'] = days_left
				else:
					req.session['sess.pwage'] = 'ok'
			else:
				req.session['sess.pwage'] = 'ok'
		else:
			req.session['sess.pwage'] = 'ok'
		return True

	def __str__(self):
		return '%s' % str(self.name)

def _sess_nextcheck(req, ts):
	cfg = req.registry.settings
	try:
		secs = int(cfg.get('netprofile.auth.session_check_period', 1800))
	except (TypeError, ValueError):
		secs = 1800
	return ts + dt.timedelta(seconds=secs)

class DAVLock(Base):
	"""
	Persistent locking primitive used in DAV access.
	"""

	SCOPE_SHARED = 0
	SCOPE_EXCLUSIVE = 1

	__tablename__ = 'dav_locks'
	__table_args__ = (
		Comment('DAV locks'),
		Index('dav_locks_i_uid', 'uid'),
		Index('dav_locks_i_token', 'token'),
		Index('dav_locks_i_timeout', 'timeout'),
		Index('dav_locks_i_fileid', 'fileid'),
		Index('dav_locks_i_uri', 'uri', mysql_length=255),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8'
		}
	)
	id = Column(
		'dlid',
		UInt32(),
		Sequence('dav_locks_dlid_seq'),
		Comment('DAV lock ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='dav_locks_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Owner\'s user ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('User')
		}
	)
	file_id = Column(
		'fileid',
		UInt32(),
		ForeignKey('files_def.fileid', name='dav_locks_fk_fileid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Linked file ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('File')
		}
	)
	timeout = Column(
		TIMESTAMP(),
		Comment('Lock timeout'),
		nullable=True,
		default=None,
#		server_default=text('NULL'),
		info={
			'header_string' : _('Timeout')
		}
	)
	creation_time = Column(
		'ctime',
		TIMESTAMP(),
		Comment('Creation timestamp'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Created')
		}
	)
	token = Column(
		Unicode(100),
		Comment('Lock token'),
		nullable=False,
		info={
			'header_string' : _('Token')
		}
	)
	owner = Column(
		Unicode(100),
		Comment('Lock owner'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Owner')
		}
	)
	scope = Column(
		Int8(),
		Comment('Lock scope'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Scope')
		}
	)
	depth = Column(
		Int8(),
		Comment('Lock depth'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Depth')
		}
	)
	uri = Column(
		Unicode(1000),
		Comment('Lock URI'),
		nullable=False,
		info={
			'header_string' : _('URI')
		}
	)

	@classmethod
	def find(cls, path, children=False):
		sess = DBSession()
		full_path = '/'.join(path)
		q = sess.query(DAVLock).filter(or_(
			DAVLock.timeout == None,
			DAVLock.timeout > func.now()
		))
		alter = [DAVLock.uri == full_path]
		for i in range(len(path) - 1):
			alter.append(and_(
				DAVLock.depth != 0,
				DAVLock.uri == '/'.join(path[:i + 1])
			))
		if children:
			alter.append(DAVLock.uri.startswith(full_path + '/'))
		return q.filter(or_(*alter))

	def get_dav_scope(self):
		if self.scope == self.SCOPE_SHARED:
			return dprops.SHARED
		if self.scope == self.SCOPE_EXCLUSIVE:
			return dprops.EXCLUSIVE
		raise ValueError('Invalid lock scope: %r' % self.scope)

	def test_token(self, value):
		if ('opaquelocktoken:%s' % self.token) == value:
			return True
		return False

	def refresh(self, new_td=None):
		old_td = None
		if self.creation_time and self.timeout:
			old_td = self.timeout - self.creation_time
		self.creation_time = dt.datetime.now()
		if new_td:
			self.timeout = self.creation_time + dt.timedelta(seconds=new_td)
		elif old_td:
			self.timeout = self.creation_time + old_td
		else:
			self.timeout = self.creation_time + dt.timedelta(seconds=1800)
		return old_td

class FileMeta(Mutable, dict):
	@classmethod
	def coerce(cls, key, value):
		if not isinstance(value, FileMeta):
			if isinstance(value, dict):
				return FileMeta(value)
			return Mutable.coerce(key, value)
		else:
			return value

	def __setitem__(self, key, value):
		dict.__setitem__(self, key, value)
		self.changed()

	def __delitem__(self, key):
		dict.__delitem__(self, key)
		self.changed()

	def __getstate__(self):
		return dict(self)

	def __setstate__(self, st):
		self.update(st)

	def get_prop(self, name):
		return self['p'][name]

	def get_props(self):
		if 'p' not in self:
			return dict()
		return self['p']

	def set_prop(self, name, value):
		if 'p' not in self:
			self['p'] = {}
		self['p'][name] = value
		self.changed()

	def del_prop(self, name):
		if ('p' not in self) or (name not in self['p']):
			return
		del self['p'][name]
		if len(self['p']) == 0:
			del self['p']
		self.changed()

class FileFolderAccessRule(DeclEnum):
	private = 'private', _('Owner-only access'), 10
	group   = 'group',   _('Group-only access'), 20
	public  = 'public',  _('Public access'),     30

@implementer(IDAVCollection)
class FileFolder(Base):
	"""
	NetProfile VFS folder definition.
	"""
	__tablename__ = 'files_folders'
	__table_args__ = (
		Comment('File folders'),
		Index('files_folders_u_folder', 'parentid', 'name', unique=True),
		Index('files_folders_i_uid', 'uid'),
		Index('files_folders_i_gid', 'gid'),
		Trigger('before', 'insert', 't_files_folders_bi'),
		Trigger('before', 'update', 't_files_folders_bu'),
		Trigger('after', 'insert', 't_files_folders_ai'),
		Trigger('after', 'update', 't_files_folders_au'),
		Trigger('after', 'delete', 't_files_folders_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_read'     : 'FILES_LIST',
				'cap_create'   : 'FILES_UPLOAD',
				'cap_edit'     : 'FILES_EDIT',
				'cap_delete'   : 'FILES_DELETE',

				'menu_name'    : _('Folders'),
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('ffid', 'name', 'parent', 'ctime', 'mtime'),
				'grid_hidden'  : ('ffid', 'parent'),
				'form_view'    : ('name', 'user', 'group', 'rights', 'ctime', 'mtime', 'descr'),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple'),
				'extra_data'   : ('allow_read', 'allow_write', 'allow_traverse')
			}
		}
	)
	id = Column(
		'ffid',
		UInt32(),
		Sequence('files_folders_ffid_seq'),
		Comment('File folder ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	parent_id = Column(
		'parentid',
		UInt32(),
		ForeignKey('files_folders.ffid', name='files_folders_fk_parentid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Parent folder ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Parent')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='files_folders_fk_uid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Owner\'s user ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('User'),
			'editor_config' : { 'allowBlank' : False }
		}
	)
	group_id = Column(
		'gid',
		UInt32(),
		ForeignKey('groups.gid', name='files_folders_fk_gid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Owner\'s group ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Group'),
			'editor_config' : { 'allowBlank' : False }
		}
	)
	rights = Column(
		UInt32(),
		Comment('Rights bitmask'),
		nullable=False,
		default=F_DEFAULT_DIRS,
		server_default=text(str(F_DEFAULT_DIRS)),
		info={
			'header_string' : _('Rights'),
			'editor_xtype'  : 'filerights',
			'editor_config' : { 'isDirectory' : True }
		}
	)
	access = Column(
		FileFolderAccessRule.db_type(),
		Comment('Folder access rule'),
		nullable=False,
		default=FileFolderAccessRule.public,
		server_default=FileFolderAccessRule.public,
		info={
			'header_string' : _('Access Rule')
		}
	)
	creation_time = Column(
		'ctime',
		TIMESTAMP(),
		Comment('Creation timestamp'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Created')
		}
	)
	modification_time = Column(
		'mtime',
		TIMESTAMP(),
		Comment('Last modification timestamp'),
		CurrentTimestampDefault(on_update=True),
		nullable=False,
#		default=zzz,
		info={
			'header_string' : _('Modified')
		}
	)
	name = Column(
		ExactUnicode(255),
		Comment('Folder name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Folder description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)
	meta = Column(
		FileMeta.as_mutable(PickleType),
		Comment('Serialized meta-data'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Metadata')
		}
	)
	files = relationship(
		'File',
		backref='folder',
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	subfolders = relationship(
		'FileFolder',
		backref=backref('parent', remote_side=[id])
	)
	root_groups = relationship(
		'Group',
		backref='root_folder',
		primaryjoin='FileFolder.id == Group.root_folder_id'
	)

	@classmethod
	def __augment_create__(cls, sess, obj, values, req):
		u = req.user
		root_ff = u.group.effective_root_folder
		if 'parentid' in values:
			pid = values['parentid']
			if pid is None:
				if not u.root_writable:
					return False
			else:
				try:
					pid = int(pid)
				except (TypeError, ValueError):
					return False
				parent = sess.query(FileFolder).get(pid)
				if parent is None:
					return False
				if (not parent.can_write(u)) or (not parent.can_traverse_path(u)):
					return False
				if root_ff and (not parent.is_inside(root_ff)):
					return False
		elif root_ff or not u.root_writable:
			return False
		return True

	@classmethod
	def __augment_update__(cls, sess, obj, values, req):
		u = req.user
		if not obj.can_write(u):
			return False
		parent = obj.parent
		if parent:
			if (not parent.can_write(u)) or (not parent.can_traverse_path(u)):
				return False
		root_ff = u.group.effective_root_folder
		if root_ff and (not obj.is_inside(root_ff)):
			return False
		if (not root_ff) and (not u.root_writable):
			return False
		if 'parentid' in values:
			pid = values['parentid']
			if pid is None:
				if not u.root_writable:
					return False
			else:
				try:
					pid = int(pid)
				except (TypeError, ValueError):
					return False
				new_parent = sess.query(FileFolder).get(pid)
				if new_parent is None:
					return False
				if (not new_parent.can_write(u)) or (not new_parent.can_traverse_path(u)):
					return False
				if root_ff and (not new_parent.is_inside(root_ff)):
					return False
		return True

	@classmethod
	def __augment_delete__(cls, sess, obj, values, req):
		u = req.user
		if not obj.can_write(u):
			return False
		parent = obj.parent
		if parent:
			if (not parent.can_write(u)) or (not parent.can_traverse_path(u)):
				return False
		root_ff = u.group.effective_root_folder
		if root_ff and (not obj.is_inside(root_ff)):
			return False
		if (not parent) and (not u.root_writable):
			return False

		# Extra precaution
		if obj.user != u:
			return False

		return True

	@property
	def __name__(self):
		return self.name

	def __iter__(self):
		for t in self.subfolders:
			yield t.name
		for t in self.files:
			yield t.filename

	def __getitem__(self, name):
		sess = DBSession()
		try:
			f = sess.query(FileFolder).filter(FileFolder.parent == self, FileFolder.name == name).one()
		except NoResultFound:
			try:
				f = sess.query(File).filter(File.folder == self, File.filename == name).one()
			except NoResultFound:
				raise KeyError('No such file or directory')
		f.__req__ = getattr(self, '__req__', None)
		f.__plugin__ = getattr(self, '__plugin__', None)
		f.__parent__ = self
		return f

	@property
	def __acl__(self):
		rights = self.rights
		if self.user:
			ff_user = 'u:%s' % self.user.login
		else:
			ff_user = 'u:'
		if self.group:
			ff_group = 'g:%s' % self.group.name
		else:
			ff_group = 'g:'
		can_access_u = None
		can_access_g = None
		can_access_o = None
		for pacl in self.__parent__.__acl__:
			if pacl[2] == 'access':
				if pacl[1] == ff_user:
					can_access_u = (True if (pacl[0] == Allow) else False)
				elif pacl[1] == ff_group:
					can_access_g = (True if (pacl[0] == Allow) else False)
				elif pacl[1] == Everyone:
					can_access_o = (True if (pacl[0] == Allow) else False)
		if can_access_g is None:
			can_access_g = can_access_o
		if can_access_u is None:
			can_access_u = can_access_o
		return (
			(Allow if ((rights & F_OWNER_EXEC) and can_access_u) else Deny, ff_user, 'access'),
			(Allow if ((rights & F_OWNER_READ) and can_access_u) else Deny, ff_user, 'read'),
			(Allow if ((rights & F_OWNER_WRITE) and can_access_u) else Deny, ff_user, 'write'),
			(Allow if ((rights & F_OWNER_EXEC) and can_access_u) else Deny, ff_user, 'execute'),
			(Allow if ((rights & F_OWNER_WRITE) and can_access_u) else Deny, ff_user, 'create'),
			(Allow if ((rights & F_OWNER_WRITE) and can_access_u) else Deny, ff_user, 'delete'),

			(Allow if ((rights & F_GROUP_EXEC) and can_access_g) else Deny, ff_group, 'access'),
			(Allow if ((rights & F_GROUP_READ) and can_access_g) else Deny, ff_group, 'read'),
			(Allow if ((rights & F_GROUP_WRITE) and can_access_g) else Deny, ff_group, 'write'),
			(Allow if ((rights & F_GROUP_EXEC) and can_access_g) else Deny, ff_group, 'execute'),
			(Allow if ((rights & F_GROUP_WRITE) and can_access_g) else Deny, ff_group, 'create'),
			(Allow if ((rights & F_GROUP_WRITE) and can_access_g) else Deny, ff_group, 'delete'),

			(Allow if ((rights & F_OTHER_EXEC) and can_access_o) else Deny, Everyone, 'access'),
			(Allow if ((rights & F_OTHER_READ) and can_access_o) else Deny, Everyone, 'read'),
			(Allow if ((rights & F_OTHER_WRITE) and can_access_o) else Deny, Everyone, 'write'),
			(Allow if ((rights & F_OTHER_EXEC) and can_access_o) else Deny, Everyone, 'execute'),
			(Allow if ((rights & F_OTHER_WRITE) and can_access_o) else Deny, Everyone, 'create'),
			(Allow if ((rights & F_OTHER_WRITE) and can_access_o) else Deny, Everyone, 'delete'),

			DENY_ALL
		)

	@property
	def dav_owner(self):
		return self.user

	@property
	def dav_group(self):
		return self.group

	def dav_acl(self, req):
		if self.user:
			ff_user = 'u:%s' % self.user.login
		else:
			ff_user = 'u:'
		if self.group:
			ff_group = 'g:%s' % self.group.name
		else:
			ff_group = 'g:'
		owner_y = []
		group_y = []
		other_y = []
		for ace in self.__acl__:
			if ace[0] != Allow:
				continue
			bucket = None
			if ace[1] == ff_user:
				bucket = owner_y
			elif ace[1] == ff_group:
				bucket = group_y
			elif ace[1] == Everyone:
				bucket = other_y
			if bucket is None:
				continue
			if ace[2] == 'read':
				bucket.append(dprops.ACL_READ)
			elif ace[2] == 'write':
				bucket.extend((
					dprops.ACL_WRITE,
					dprops.ACL_WRITE_CONTENT,
					dprops.ACL_WRITE_PROPERTIES
				))
			elif ace[2] == 'create':
				bucket.append(dprops.ACL_BIND)
			elif ace[2] == 'delete':
				bucket.append(dprops.ACL_UNBIND)
			# TODO: access, execute
		aces = []
		if len(owner_y):
			aces.append(DAVACEValue(
				DAVPrincipalValue(DAVPrincipalValue.PROPERTY, prop=dprops.OWNER),
				grant=owner_y,
				protected=True
			))
		if len(group_y):
			aces.append(DAVACEValue(
				DAVPrincipalValue(DAVPrincipalValue.PROPERTY, prop=dprops.GROUP),
				grant=group_y,
				protected=True
			))
		if len(other_y):
			aces.append(DAVACEValue(
				DAVPrincipalValue(DAVPrincipalValue.ALL),
				grant=other_y,
				protected=True
			))
		return DAVACLValue(aces)

	def get_uri(self):
		p = getattr(self, '__parent__', None)
		if p is None:
			p = self.parent
		if p is None:
			return [ '', 'fs', self.name ]
		uri = p.get_uri()
		uri.append(self.name)
		return uri

	def dav_props(self, pset):
		ret = {}
		if dprops.RESOURCE_TYPE in pset:
			ret[dprops.RESOURCE_TYPE] = DAVResourceTypeValue(dprops.COLLECTION)
		if dprops.CREATION_DATE in pset:
			ret[dprops.CREATION_DATE] = self.creation_time
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = self.name
		if dprops.LAST_MODIFIED in pset:
			ret[dprops.LAST_MODIFIED] = self.modification_time
		if dprops.IS_COLLECTION in pset:
			ret[dprops.IS_COLLECTION] = '1'
		if dprops.IS_FOLDER in pset:
			ret[dprops.IS_FOLDER] = 't'
		if dprops.IS_HIDDEN in pset:
			ret[dprops.IS_HIDDEN] = '0'
		if isinstance(pset, DAVAllPropsSet):
			ret.update(self.get_props())
		else:
			custom = pset.difference(dprops.RO_PROPS)
			for cprop in custom:
				try:
					ret[cprop] = self.get_prop(cprop)
				except KeyError:
					pass
		return ret

	def dav_props_set(self, pdict):
		pset = set(pdict)
		custom = pset.difference(dprops.RO_PROPS)
		for cprop in custom:
			if pdict[cprop] is None:
				self.del_prop(cprop)
			else:
				self.set_prop(cprop, pdict[cprop])
		return True

	def get_prop(self, name):
		if not self.meta:
			self.meta = FileMeta()
		return self.meta.get_prop(name)

	def get_props(self):
		if not self.meta:
			self.meta = FileMeta()
		return self.meta.get_props()

	def set_prop(self, name, value):
		if not self.meta:
			self.meta = FileMeta()
		return self.meta.set_prop(name, value)

	def del_prop(self, name):
		if not self.meta:
			self.meta = FileMeta()
		return self.meta.del_prop(name)

	def dav_create(self, req, name, rtype=None, props=None, data=None):
		# TODO: externalize type resolution
		user = req.user
		sess = DBSession()
		if rtype and (dprops.COLLECTION in rtype):
			obj = FileFolder(
				user_id=user.id,
				group_id=user.group_id,
				name=name,
				parent=self,
				rights=F_DEFAULT_DIRS
			)
			sess.add(obj)
		else:
			obj = File(
				user_id=user.id,
				group_id=user.group_id,
				filename=name,
				name=name,
				folder=self,
				rights=F_DEFAULT_FILES
			)
			sess.add(obj)
			if props and (dprops.CONTENT_TYPE in props):
				obj.mime_type = props[dprops.CONTENT_TYPE]
			if data is not None:
				# TODO: detect type of data (fd / buffer)
				obj.set_from_file(data, user, sess)
		if props:
			if dprops.CREATION_DATE in props:
				obj.creation_time = props[dprops.CREATION_DATE]
			if dprops.LAST_MODIFIED in props:
				obj.modification_time = props[dprops.LAST_MODIFIED]
		return obj

	def dav_append(self, req, ctx, name):
		if isinstance(ctx, File):
			ctx.folder = self
			ctx.filename = name
		elif isinstance(ctx, FileFolder):
			if self.is_inside(ctx):
				raise ValueError('Infinite folder loop detected.')
			ctx.parent = self
			ctx.name = name

	def dav_clone(self, req):
		# TODO: clone meta
		obj = FileFolder(
			parent_id=None,
			name=self.name,
			user_id=self.user_id,
			group_id=self.group_id,
			rights=self.rights,
			access=self.access,
			description=self.description
		)
		return obj

	@property
	def dav_children(self):
		for t in itertools.chain(self.subfolders, self.files):
			t.__req__ = getattr(self, '__req__', None)
			t.__plugin__ = getattr(self, '__plugin__', None)
			t.__parent__ = self
			yield t

	def allow_read(self, req):
		return self.can_read(req.user)

	def allow_write(self, req):
		return self.can_write(req.user)

	def allow_traverse(self, req):
		return self.can_traverse_path(req.user)

	def can_read(self, user):
		if self.user_id == user.id:
			return bool(self.rights & F_OWNER_READ)
		if self.group_id in user.group_vector():
			return bool(self.rights & F_GROUP_READ)
		return bool(self.rights & F_OTHER_READ)

	def can_write(self, user):
		if self.user_id == user.id:
			return bool(self.rights & F_OWNER_WRITE)
		if self.group_id in user.group_vector():
			return bool(self.rights & F_GROUP_WRITE)
		return bool(self.rights & F_OTHER_WRITE)

	def can_traverse(self, user):
		if self.user_id == user.id:
			return bool(self.rights & F_OWNER_EXEC)
		if self.group_id in user.group_vector():
			return bool(self.rights & F_GROUP_EXEC)
		return bool(self.rights & F_OTHER_EXEC)

	def can_traverse_path(self, user):
		if not self.can_traverse(user):
			return False
		if user.group and (self == user.group.effective_root_folder):
			return True
		if self.parent:
			return self.parent.can_traverse_path(user)
		return True

	def is_inside(self, cont):
		par = self
		while par:
			if par.id == cont.id:
				return True
			par = par.parent
		return False

	def __str__(self):
		return '%s' % str(self.name)

_BLOCK_SIZE = 4096 * 64 # 256K
_CHUNK_SIZE = 1024 * 1024 * 2 # 2M

class WindowFileIter(FileIter):
	def __init__(self, f, block_size=_BLOCK_SIZE, window=None):
		super(WindowFileIter, self).__init__(f, block_size)
		self.window = window

	def next(self):
		if self.window is None:
			return super(WindowFileIter, self).next()
		if self.window <= 0:
			raise StopIteration
		to_read = self.block_size
		if to_read > self.window:
			to_read = self.window
		val = self.file.read(to_read)
		if not val:
			raise StopIteration
		self.window -= len(val)
		return val

	__next__ = next

class FileResponse(Response):
	def __init__(self, obj, request=None, cache_max_age=None, content_encoding=None):
		super(FileResponse, self).__init__(conditional_response=True)
		self.last_modified = obj.modification_time
		self.content_type = obj.plain_mime_type
		self.charset = obj.mime_charset
		self.allow = ('GET', 'HEAD')
		self.vary = ('Cookie',)
		# TODO: self.cache_control
		self.accept_ranges = 'bytes'
		self.headerlist.append(('X-Frame-Options', 'SAMEORIGIN'))
		if PY3:
			self.content_disposition = \
				'attachment; filename*=UTF-8\'\'%s' % (
					urllib.parse.quote(obj.filename, '')
				)
		else:
			self.content_disposition = \
				'attachment; filename*=UTF-8\'\'%s' % (
					urllib.quote(obj.filename.encode(), '')
				)
		self.etag = obj.etag
		self.content_encoding = content_encoding
		cr = None
		if request.range and (self in request.if_range) and (',' not in request.headers.get('Range')):
			cr = request.range.content_range(length=obj.size)
		if cr:
			self.status = 206
			self.content_range = cr
		elif obj.size:
			self.content_range = (0, obj.size, obj.size)
			if request.range and ('If-Range' not in request.headers):
				self.status = 416
				self.content_range = 'bytes */%d' % obj.size

		if request.method != 'HEAD':
			bio = None
			app_iter = None
			data = obj.data
			if data is None:
				bio = obj.open('r')
				if cr:
					bio.seek(cr.start)
					self.app_iter = WindowFileIter(bio, _BLOCK_SIZE, cr.stop - cr.start)
				else:
					if request is not None:
						environ = request.environ
						if 'wsgi.file_wrapper' in environ:
							app_iter = environ['wsgi.file_wrapper'](bio, _BLOCK_SIZE)
					if app_iter is None:
						app_iter = FileIter(bio, _BLOCK_SIZE)
					self.app_iter = app_iter
			else:
				if cr:
					bio = io.BytesIO(obj.data[cr.start:cr.stop])
				else:
					bio = io.BytesIO(obj.data)
				if request is not None:
					environ = request.environ
					if 'wsgi.file_wrapper' in environ:
						app_iter = environ['wsgi.file_wrapper'](bio, _BLOCK_SIZE)
				if app_iter is None:
					app_iter = FileIter(bio, _BLOCK_SIZE)
				self.app_iter = app_iter

		if cr:
			self.content_length = (cr.stop - cr.start)
		else:
			self.content_length = obj.size
		if cache_max_age is not None:
			self.cache_expires = cache_max_age

_re_charset = re.compile(r'charset=([\w\d_-]+)')

@implementer(IDAVFile)
class File(Base):
	"""
	NetProfile VFS file definition.
	"""
	__tablename__ = 'files_def'
	__table_args__ = (
		Comment('Stored files'),
		Index('files_def_u_file', 'ffid', 'fname', unique=True),
		Index('files_def_i_uid', 'uid'),
		Index('files_def_i_gid', 'gid'),
		Index('files_def_i_ffid', 'ffid'),
		Trigger('before', 'insert', 't_files_def_bi'),
		Trigger('before', 'update', 't_files_def_bu'),
		Trigger('after', 'insert', 't_files_def_ai'),
		Trigger('after', 'update', 't_files_def_au'),
		Trigger('after', 'delete', 't_files_def_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_read'     : 'FILES_LIST',
				'cap_create'   : 'FILES_UPLOAD',
				'cap_edit'     : 'FILES_EDIT',
				'cap_delete'   : 'FILES_DELETE',

				'menu_name'    : _('Files'),
				'default_sort' : ({ 'property': 'fname' ,'direction': 'ASC' },),
				'grid_view'    : ('fileid', 'folder', 'fname', 'size', 'ctime', 'mtime'),
				'grid_hidden'  : ('fileid',),
				'form_view'    : ('fname', 'folder', 'size', 'user', 'group', 'rights', 'ctime', 'mtime', 'name', 'descr'),
				'easy_search'  : ('fname', 'name'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple'),
				'extra_data'   : ('allow_access', 'allow_read', 'allow_write', 'allow_execute')
			}
		}
	)
	id = Column(
		'fileid',
		UInt32(),
		Sequence('files_def_fileid_seq'),
		Comment('File ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	folder_id = Column(
		'ffid',
		UInt32(),
		ForeignKey('files_folders.ffid', name='files_def_fk_ffid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Parent folder ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Folder'),
			'filter_type'   : 'list'
		}
	)
	filename = Column(
		'fname',
		ExactUnicode(255),
		Comment('File name'),
		nullable=False,
		info={
			'header_string' : _('Filename')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Human-readable file name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='files_def_fk_uid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Owner\'s user ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('User'),
			'editor_config' : { 'allowBlank' : False }
		}
	)
	group_id = Column(
		'gid',
		UInt32(),
		ForeignKey('groups.gid', name='files_def_fk_gid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Owner\'s group ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Group'),
			'editor_config' : { 'allowBlank' : False }
		}
	)
	rights = Column(
		UInt32(),
		Comment('Rights bitmask'),
		nullable=False,
		default=F_DEFAULT_FILES,
		server_default=text(str(F_DEFAULT_FILES)),
		info={
			'header_string' : _('Rights'),
			'editor_xtype'  : 'filerights'
		}
	)
	mime_type = Column(
		'mime',
		ASCIIString(255),
		Comment('MIME type of the file'),
		nullable=False,
		default='application/octet-stream',
		server_default='application/octet-stream',
		info={
			'header_string' : _('Type')
		}
	)
	size = Column(
		UInt32(),
		Comment('File size (in bytes)'),
		nullable=False,
		info={
			'header_string' : _('Size'),
			'read_only'     : True
		}
	)
	creation_time = Column(
		'ctime',
		TIMESTAMP(),
		Comment('Creation timestamp'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Created'),
			'read_only'     : True
		}
	)
	modification_time = Column(
		'mtime',
		TIMESTAMP(),
		Comment('Last modification timestamp'),
		CurrentTimestampDefault(on_update=True),
		nullable=False,
#		default=zzz,
		info={
			'header_string' : _('Modified'),
			'read_only'     : True
		}
	)
	etag = Column(
		ASCIIString(255),
		Comment('Generated file ETag'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('E-Tag'),
			'read_only'     : True
		}
	)
	read_count = Column(
		'rcount',
		UInt32(),
		Comment('Current read count'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Read Count')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('File description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)
	meta = Column(
		FileMeta.as_mutable(PickleType),
		Comment('Serialized meta-data'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Metadata')
		}
	)
	data = deferred(Column(
		LargeBLOB(),
		Comment('Actual file data'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Data')
		}
	))

	chunks = relationship(
		'FileChunk',
		backref=backref('file', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	locks = relationship(
		'DAVLock',
		backref='file',
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	@classmethod
	def __augment_create__(cls, sess, obj, values, req):
		u = req.user
		root_ff = u.group.effective_root_folder
		if 'ffid' in values:
			ffid = values['ffid']
			if ffid is None:
				if not u.root_writable:
					return False
			else:
				try:
					ffid = int(ffid)
				except (TypeError, ValueError):
					return False
				parent = sess.query(FileFolder).get(ffid)
				if parent is None:
					return False
				if (not parent.can_write(u)) or (not parent.can_traverse_path(u)):
					return False
				if root_ff and (not parent.is_inside(root_ff)):
					return False
		elif root_ff or not u.root_writable:
			return False
		return True

	@classmethod
	def __augment_update__(cls, sess, obj, values, req):
		u = req.user
		if not obj.can_write(u):
			return False
		parent = obj.folder
		if parent:
			if (not parent.can_write(u)) or (not parent.can_traverse_path(u)):
				return False
		root_ff = u.group.effective_root_folder
		if root_ff and (not obj.is_inside(root_ff)):
			return False
		if (not root_ff) and (not u.root_writable):
			return False
		if 'ffid' in values:
			ffid = values['ffid']
			if ffid is None:
				if not u.root_writable:
					return False
			else:
				try:
					ffid = int(ffid)
				except (TypeError, ValueError):
					return False
				new_parent = sess.query(FileFolder).get(ffid)
				if new_parent is None:
					return False
				if (not new_parent.can_write(u)) or (not new_parent.can_traverse_path(u)):
					return False
				if root_ff and (not new_parent.is_inside(root_ff)):
					return False
		return True

	@classmethod
	def __augment_delete__(cls, sess, obj, values, req):
		u = req.user
		if not obj.can_write(u):
			return False
		parent = obj.folder
		if parent:
			if (not parent.can_write(u)) or (not parent.can_traverse_path(u)):
				return False
		root_ff = u.group.effective_root_folder
		if root_ff and (not obj.is_inside(root_ff)):
			return False
		if (not parent) and (not u.root_writable):
			return False
		return True

	@property
	def plain_mime_type(self):
		return self.mime_type.split(';')[0]

	@property
	def mime_class(self):
		return self.mime_type.split('/')[0]

	@property
	def mime_charset(self):
		if not self.mime_type:
			return None
		csm = _re_charset.search(self.mime_type)
		if csm:
			cset = csm.group(1)
			if cset in {'binary', 'unknown-8bit'}:
				return None
			return cset

	@property
	def __name__(self):
		return self.filename

	@property
	def __acl__(self):
		rights = self.rights
		if self.user:
			ff_user = 'u:%s' % self.user.login
		else:
			ff_user = 'u:'
		if self.group:
			ff_group = 'g:%s' % self.group.name
		else:
			ff_group = 'g:'
		can_access_u = None
		can_access_g = None
		can_access_o = None
		for pacl in self.__parent__.__acl__:
			if pacl[2] == 'access':
				if pacl[1] == ff_user:
					can_access_u = (True if (pacl[0] == Allow) else False)
				elif pacl[1] == ff_group:
					can_access_g = (True if (pacl[0] == Allow) else False)
				elif pacl[1] == Everyone:
					can_access_o = (True if (pacl[0] == Allow) else False)
		if can_access_g is None:
			can_access_g = can_access_o
		if can_access_u is None:
			can_access_u = can_access_o
		return (
			(Allow if ((rights & F_OWNER_READ) and can_access_u) else Deny, ff_user, 'access'),
			(Allow if ((rights & F_OWNER_READ) and can_access_u) else Deny, ff_user, 'read'),
			(Allow if ((rights & F_OWNER_WRITE) and can_access_u) else Deny, ff_user, 'write'),
			(Allow if ((rights & F_OWNER_EXEC) and can_access_u) else Deny, ff_user, 'execute'),

			(Allow if ((rights & F_GROUP_READ) and can_access_g) else Deny, ff_group, 'access'),
			(Allow if ((rights & F_GROUP_READ) and can_access_g) else Deny, ff_group, 'read'),
			(Allow if ((rights & F_GROUP_WRITE) and can_access_g) else Deny, ff_group, 'write'),
			(Allow if ((rights & F_GROUP_EXEC) and can_access_g) else Deny, ff_group, 'execute'),

			(Allow if ((rights & F_OTHER_READ) and can_access_o) else Deny, Everyone, 'access'),
			(Allow if ((rights & F_OTHER_READ) and can_access_o) else Deny, Everyone, 'read'),
			(Allow if ((rights & F_OTHER_WRITE) and can_access_o) else Deny, Everyone, 'write'),
			(Allow if ((rights & F_OTHER_EXEC) and can_access_o) else Deny, Everyone, 'execute'),

			DENY_ALL
		)

	def get_uri(self):
		p = getattr(self, '__parent__', None)
		if p is None:
			p = self.folder
		if p is None:
			return [ self.filename ]
		uri = p.get_uri()
		uri.append(self.filename)
		return uri

	@property
	def dav_owner(self):
		return self.user

	@property
	def dav_group(self):
		return self.group

	def dav_acl(self, req):
		if self.user:
			ff_user = 'u:%s' % self.user.login
		else:
			ff_user = 'u:'
		if self.group:
			ff_group = 'g:%s' % self.group.name
		else:
			ff_group = 'g:'
		owner_y = []
		group_y = []
		other_y = []
		for ace in self.__acl__:
			if ace[0] != Allow:
				continue
			bucket = None
			if ace[1] == ff_user:
				bucket = owner_y
			elif ace[1] == ff_group:
				bucket = group_y
			elif ace[1] == Everyone:
				bucket = other_y
			if bucket is None:
				continue
			if ace[2] == 'read':
				bucket.append(dprops.ACL_READ)
			elif ace[2] == 'write':
				bucket.extend((
					dprops.ACL_WRITE,
					dprops.ACL_WRITE_CONTENT,
					dprops.ACL_WRITE_PROPERTIES
				))
			# TODO: access, execute
		aces = []
		if len(owner_y):
			aces.append(DAVACEValue(
				DAVPrincipalValue(DAVPrincipalValue.PROPERTY, prop=dprops.OWNER),
				grant=owner_y,
				protected=True
			))
		if len(group_y):
			aces.append(DAVACEValue(
				DAVPrincipalValue(DAVPrincipalValue.PROPERTY, prop=dprops.GROUP),
				grant=group_y,
				protected=True
			))
		if len(other_y):
			aces.append(DAVACEValue(
				DAVPrincipalValue(DAVPrincipalValue.ALL),
				grant=other_y,
				protected=True
			))
		return DAVACLValue(aces)

	def dav_props(self, pset):
		ret = {}
		if dprops.RESOURCE_TYPE in pset:
			ret[dprops.RESOURCE_TYPE] = DAVResourceTypeValue()
		if dprops.CONTENT_LENGTH in pset:
			ret[dprops.CONTENT_LENGTH] = self.size
		if dprops.CONTENT_TYPE in pset:
			ret[dprops.CONTENT_TYPE] = self.plain_mime_type
		if dprops.CREATION_DATE in pset:
			ret[dprops.CREATION_DATE] = self.creation_time
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = self.filename
		if dprops.ETAG in pset:
			etag = None
			if self.etag:
				etag = '"%s"' % self.etag
			ret[dprops.ETAG] = etag
		if hasattr(self, '__req__'):
			req = self.__req__
			if dprops.EXECUTABLE in pset:
				ret[dprops.EXECUTABLE] = 'T' if self.can_execute(req.user) else 'F'
		if dprops.LAST_MODIFIED in pset:
			ret[dprops.LAST_MODIFIED] = self.modification_time
		if isinstance(pset, DAVAllPropsSet):
			ret.update(self.get_props())
		else:
			custom = pset.difference(dprops.RO_PROPS)
			for cprop in custom:
				try:
					ret[cprop] = self.get_prop(cprop)
				except KeyError:
					pass
		return ret

	def dav_props_set(self, pdict):
		pset = set(pdict)
		custom = pset.difference(dprops.RO_PROPS)
		for cprop in custom:
			if pdict[cprop] is None:
				self.del_prop(cprop)
			else:
				self.set_prop(cprop, pdict[cprop])
		return True

	def get_prop(self, name):
		if not self.meta:
			self.meta = FileMeta()
		return self.meta.get_prop(name)

	def get_props(self):
		if not self.meta:
			self.meta = FileMeta()
		return self.meta.get_props()

	def set_prop(self, name, value):
		if not self.meta:
			self.meta = FileMeta()
		return self.meta.set_prop(name, value)

	def del_prop(self, name):
		if not self.meta:
			self.meta = FileMeta()
		return self.meta.del_prop(name)

	def dav_get(self, req):
		return self.get_response(req)

	def dav_put(self, req, data, start=None, length=None):
		self.etag = None
		if isinstance(start, int) and isinstance(length, int):
			self.set_region_from_file(data, start, length, req.user)
		else:
			self.set_from_file(data, req.user)

	def dav_clone(self, req):
		# TODO: clone meta
		obj = File(
			folder_id=self.folder_id,
			filename=self.filename,
			name=self.name,
			user_id=self.user_id,
			group_id=self.group_id,
			rights=self.rights,
			mime_type=self.mime_type,
			size=0,
			etag=None,
			description=self.description
		)
		obj.set_from_object(self, req.user)
		return obj

	def allow_access(self, req):
		return self.can_access(req.user)

	def allow_read(self, req):
		return self.can_read(req.user)

	def allow_write(self, req):
		return self.can_write(req.user)

	def allow_execute(self, req):
		return self.can_execute(req.user)

	def can_access(self, user):
		if self.folder:
			return self.folder.can_traverse_path(user)
		return True

	def can_read(self, user):
		if self.user_id == user.id:
			return bool(self.rights & F_OWNER_READ)
		if self.group_id in user.group_vector():
			return bool(self.rights & F_GROUP_READ)
		return bool(self.rights & F_OTHER_READ)

	def can_write(self, user):
		if self.user_id == user.id:
			return bool(self.rights & F_OWNER_WRITE)
		if self.group_id in user.group_vector():
			return bool(self.rights & F_GROUP_WRITE)
		return bool(self.rights & F_OTHER_WRITE)

	def can_execute(self, user):
		if self.user_id == user.id:
			return bool(self.rights & F_OWNER_EXEC)
		if self.group_id in user.group_vector():
			return bool(self.rights & F_GROUP_EXEC)
		return bool(self.rights & F_OTHER_EXEC)

	def is_inside(self, cont):
		if (self.folder_id is None) and (cont is None):
			return True
		par = self.folder
		while par:
			if par.id == cont.id:
				return True
			par = par.parent
		return False

	def get_response(self, req):
		return FileResponse(self, req)

	def open(self, mode='r', user_perm=None, sess=None):
		xm = 0
		if 'r+' in mode:
			xm |= _VFS_READ|_VFS_WRITE
		elif 'w+' in mode:
			xm |= _VFS_READ|_VFS_WRITE|_VFS_TRUNCATE
		elif 'a+' in mode:
			xm |= _VFS_READ|_VFS_WRITE|_VFS_APPEND
		elif 'r' in mode:
			xm |= _VFS_READ
		elif 'w' in mode:
			xm |= _VFS_WRITE
		elif 'a' in mode:
			xm |= _VFS_WRITE|_VFS_APPEND
		if user_perm:
			if (xm & _VFS_READ) and not self.can_read(user_perm):
				raise IOError(errno.EACCES, 'Read access denied', self)
			if (xm & _VFS_WRITE) and not self.can_write(user_perm):
				raise IOError(errno.EACCES, 'Write access denied', self)
		return VFSFileIO(self, xm, sess)

	@validates('data')
	def _set_data(self, k, v):
		if v is None:
			return None
		ctx = hashlib.md5()
		ctx.update(v)
		self.etag = ctx.hexdigest()
		self.size = len(v)
		m = magic.get()
		guessed_mime = m.buffer(v)
		if guessed_mime:
			self.mime_type = guessed_mime
		return v

	def set_from_file(self, infile, user=None, sess=None):
		if sess is None:
			sess = DBSession()
		m = magic.get()
		self.size = 0
		fd = -1
		buf = bytearray(_BLOCK_SIZE)
		mv = memoryview(buf)
		ctx = hashlib.md5()
		with self.open('w+', user, sess) as fd:
			while 1:
				rsz = infile.readinto(buf)
				if not rsz:
					break
				ctx.update(mv[:rsz])
				fd.write(mv[:rsz])
		self.etag = ctx.hexdigest()
		self.data = None
		infile.seek(0)
		try:
			fd = infile.fileno()
			guessed_mime = m.descriptor(fd)
		except:
			guessed_mime = m.buffer(infile.read())
		if guessed_mime:
			self.mime_type = guessed_mime

	def set_region_from_file(self, infile, start, length, user=None, sess=None):
		if sess is None:
			sess = DBSession()
		fd = -1
		buf = bytearray(_BLOCK_SIZE)
		mv = memoryview(buf)
		ctx = hashlib.md5()
		with self.open('w+', user, sess) as fd:
			fd.seek(start)
			while 1:
				rsz = infile.readinto(buf)
				if not rsz:
					break
				if rsz > length:
					ctx.update(mv[:length])
					fd.write(mv[:length])
					break
				ctx.update(mv[:rsz])
				fd.write(mv[:rsz])
				length -= rsz
		self.etag = ctx.hexdigest()
		self.data = None

	def set_from_object(self, infile, user=None, sess=None):
		if sess is None:
			sess = DBSession()
		self.size = 0
		self.etag = None
		buf = bytearray(_BLOCK_SIZE)
		mv = memoryview(buf)
		with self.open('w+', user, sess) as fd:
			with infile.open('r', user, sess) as infd:
				while 1:
					rsz = infd.readinto(buf)
					if not rsz:
						break
					fd.write(mv[:rsz])
		self.etag = infile.etag
		self.data = None
		self.mime_type = infile.mime_type

	def get_data(self):
		if self.data:
			return self.data
		with self.open('r') as fd:
			return fd.read()

	def __str__(self):
		return '%s' % str(self.filename)

class FileChunk(Base):
	"""
	Single chunk of a VFS file. Contains _CHUNK_SIZE bytes.
	"""
	__tablename__ = 'files_chunks'
	__table_args__ = (
		Comment('Stored file chunks'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'BASE_ADMIN',
				'cap_create'    : '__NOPRIV__',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : '__NOPRIV__'
			}
		}
	)
	file_id = Column(
		'fileid',
		UInt32(),
		ForeignKey('files_def.fileid', name='files_chunks_fk_fileid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('File ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	offset = Column(
		UInt32(),
		Comment('File chunk offset'),
		primary_key=True,
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Offset')
		}
	)
	# needs deferred? maybe not
	data = Column(
		LargeBLOB(),
		Comment('File chunk data'),
		nullable=False,
		info={
			'header_string' : _('Data')
		}
	)

	def get_buffer(self):
		try:
			return self._buf
		except AttributeError:
			pass
		if self.data:
			self._buf = bytearray(self.data)
		else:
			self._buf = bytearray()
		return self._buf

	def sync_buffer(self):
		if not hasattr(self, '_buf'):
			raise ValueError()
		if self.file and self.file.etag:
			ctx = hashlib.md5()
			ctx.update(self.file.etag.encode())
			ctx.update(self._buf)
			self.file.etag = ctx.hexdigest()
		self.data = bytes(self._buf)

class VFSFileIO(io.BufferedIOBase):
	"""
	VFS file handle.
	"""
	def __init__(self, fo, mode=_VFS_READ, sess=None):
		if sess is None:
			xsess = DBSession()
			xsess.expunge(fo)
			self.own_sess = True
		else:
			self.own_sess = False
		# File mode internal bitmask
		self._mode = mode
		# DB session
		self._sess = sess
		# File object
		self.f = fo
		# Current chunk
		self.c = None
		# Last chunk number that we tried to load
		self.last_c = None
		# Set to true on chunk modification, to false on chunk load
		self.mod_c = False
		# Current memoryview (if it exists)
		self.buf = None
		# Offset in chunks
		self.c_offset = 0
		# Offset from chunk start
		self.b_offset = 0

		if self._mode & _VFS_TRUNCATE:
			self.truncate(0)

	@property
	def sess(self):
		if self._sess is None:
			self._sess = DBSession()
		return self._sess

	@property
	def name(self):
		return self.f.filename

	@property
	def mode(self):
		if self._mode & _VFS_APPEND:
			if self._mode & _VFS_READ:
				return 'a+'
			return 'a'
		if self._mode & _VFS_TRUNCATE:
			return 'w+'
		if self._mode & _VFS_WRITE:
			if self._mode & _VFS_READ:
				return 'r+'
			return 'w'
		if self._mode & _VFS_READ:
			return 'r'
		raise ValueError('Invalid file mode')

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, trace):
		self.close()

	def _update_chunk(self):
		if self.c and (self.c.offset != self.c_offset):
			if (self._mode & _VFS_WRITE) and self.mod_c:
				self.c.sync_buffer()
				self.sess.flush(objects=(self.c,))
			self.sess.expunge(self.c)
			self.c = None
			self.last_c = None
		self.mod_c = False
		if (self.c is None) and (self.last_c != self.c_offset):
			self.c = self.sess.query(FileChunk).get((self.f.id, self.c_offset))
			self.last_c = self.c_offset
			if self.c:
				if self._mode & _VFS_WRITE:
					self.buf = self.c.get_buffer()
				else:
					self.buf = self.c.data
			else:
				self.buf = None

	def closed(self):
		return (self.f is None)

	def close(self):
		if self._mode & _VFS_WRITE:
			self.flush()
		elif self.own_sess:
			self.sess.rollback()
		self.buf = None
		self.c = None
		self.f = None
		self.c_offset = 0
		self.b_offset = 0

	def fileno(self):
		raise IOError(errno.EBADF, 'VFS objects don\'t have file descriptors', self.f)

	def flush(self):
		if (self._mode & _VFS_WRITE) and self.c and self.mod_c:
			self.c.sync_buffer()
			self.sess.flush(objects=(self.c,))
			if self.own_sess:
				self.sess.commit()
			self.mod_c = False

	def isatty(self):
		return False

	def seekable(self):
		return True

	def seek(self, off=0, whence=0):
		old = self.tell()
		if whence == 0:
			new = off
		elif whence == 1:
			new = old + off
		elif whence == 2:
			new = self.f.size + off
		else:
			new = old
		if (new > self.f.size) and not (self._mode & _VFS_WRITE):
			new = self.f.size
		self.c_offset, self.b_offset = divmod(new, _CHUNK_SIZE)
		return new

	def tell(self):
		return self.c_offset * _CHUNK_SIZE + self.b_offset

	def truncate(self, sz=None):
		if sz == self.f.size:
			return sz
		if sz < 0:
			raise IOError(errno.EINVAL, 'New file size can\'t be negative', self.f)
		if not (self._mode & _VFS_WRITE):
			raise IOError(errno.EBADF, 'File is not open for writing', self.f)
		if sz is None:
			sz = self.c_offset * _CHUNK_SIZE + self.b_offset
			end_c, end_b = self.c_offset, self.b_offset
		else:
			end_c, end_b = divmod(sz, _CHUNK_SIZE)
		cur_c, cur_b = self.c_offset, self.b_offset
		if sz > self.f.size:
			self.f.size = sz
			return sz
		if self.mod_c:
			self.flush()
		if end_b == 0:
			self.sess.query(FileChunk) \
				.filter(FileChunk.file_id == self.f.id, FileChunk.offset >= end_c) \
				.delete()
		else:
			self.sess.query(FileChunk) \
				.filter(FileChunk.file_id == self.f.id, FileChunk.offset > end_c) \
				.delete()
			self.c_offset = end_c
			self.b_offset = end_b
			self._update_chunk()
			if self.c and (len(self.buf) > self.b_offset):
				del self.buf[self.b_offset:]
				self.mod_c = True
		self.c_offset = cur_c
		self.b_offset = cur_b
		self.f.size = sz
		return sz

	def detach(self):
		raise io.UnsupportedOperation(errno.EBADF, 'Can\'t detach chunk. Data will not be complete.', self.f)

	def readable(self):
		return (self._mode & _VFS_READ)

	def read(self, maxb=-1):
		if not (self._mode & _VFS_READ):
			raise IOError(errno.EBADF, 'File is not open for reading', self.f)
		cur_pos = self.c_offset * _CHUNK_SIZE + self.b_offset
		read_sz = self.f.size - cur_pos
		if maxb is None:
			maxb = -1
		if (maxb == 0) or (read_sz <= 0):
			return b''
		if (maxb > 0) and (read_sz > maxb):
			read_sz = maxb
		retbuf = bytearray(read_sz)
		cursor = 0
		while read_sz > 0:
			self._update_chunk()
			if self.c is None:
				to_read = min(read_sz, _CHUNK_SIZE - self.b_offset)
				read_sz -= to_read
				cursor += to_read
				self.b_offset += to_read
				if self.b_offset >= _CHUNK_SIZE:
					self.c_offset += 1
					self.b_offset = 0
				continue
			chunk_len = len(self.buf)
			if self.b_offset >= chunk_len:
				to_read = min(read_sz, _CHUNK_SIZE - self.b_offset)
				read_sz -= to_read
				cursor += to_read
				self.b_offset += to_read
				if self.b_offset >= _CHUNK_SIZE:
					self.c_offset += 1
					self.b_offset = 0
				continue
			to_read = min(chunk_len - self.b_offset, read_sz)
			mv = memoryview(self.buf)
			retbuf[cursor:cursor + to_read] = mv[self.b_offset:self.b_offset + to_read]
			read_sz -= to_read
			cursor += to_read
			self.b_offset += to_read
			if self.b_offset >= _CHUNK_SIZE:
				self.c_offset += 1
				self.b_offset = 0
		return bytes(retbuf)

	def read1(self, maxb=-1):
		if not (self._mode & _VFS_READ):
			raise IOError(errno.EBADF, 'File is not open for reading', self.f)
		raise NotImplementedError

	def readinto(self, retbuf):
		if not (self._mode & _VFS_READ):
			raise IOError(errno.EBADF, 'File is not open for reading', self.f)
		cur_pos = self.c_offset * _CHUNK_SIZE + self.b_offset
		read_sz = len(retbuf)
		file_sz = self.f.size - cur_pos
		if file_sz < read_sz:
			read_sz = file_sz
		cursor = 0
		orig_read_sz = read_sz
		while read_sz > 0:
			self._update_chunk()
			if self.c is None:
				to_read = min(read_sz, _CHUNK_SIZE - self.b_offset)
				retbuf[cursor:cursor + to_read] = (0 for x in range(to_read))
				read_sz -= to_read
				cursor += to_read
				self.b_offset += to_read
				if self.b_offset >= _CHUNK_SIZE:
					self.c_offset += 1
					self.b_offset = 0
				continue
			chunk_len = len(self.buf)
			if self.b_offset >= chunk_len:
				to_read = min(read_sz, _CHUNK_SIZE - self.b_offset)
				retbuf[cursor:cursor + to_read] = (0 for x in range(to_read))
				read_sz -= to_read
				cursor += to_read
				self.b_offset += to_read
				if self.b_offset >= _CHUNK_SIZE:
					self.c_offset += 1
					self.b_offset = 0
				continue
			to_read = min(chunk_len - self.b_offset, read_sz)
			mv = memoryview(self.buf)
			retbuf[cursor:cursor + to_read] = mv[self.b_offset:self.b_offset + to_read]
			read_sz -= to_read
			cursor += to_read
			self.b_offset += to_read
			if self.b_offset >= _CHUNK_SIZE:
				self.c_offset += 1
				self.b_offset = 0
		return orig_read_sz

	def readline(self, limit=-1):
		if not (self._mode & _VFS_READ):
			raise IOError(errno.EBADF, 'File is not open for reading', self.f)
		raise NotImplementedError

	def readlines(self, hint=-1):
		if not (self._mode & _VFS_READ):
			raise IOError(errno.EBADF, 'File is not open for reading', self.f)
		raise NotImplementedError

	readall = read

	def writable(self):
		return (self._mode & _VFS_WRITE)

	def write(self, b):
		if not (self._mode & _VFS_WRITE):
			raise IOError(errno.EBADF, 'File is not open for writing', self.f)
		write_sz = len(b)
		if write_sz == 0:
			return 0
		srcmv = memoryview(b)
		orig_write_sz = write_sz
		cur_pos = self.c_offset * _CHUNK_SIZE + self.b_offset
		cursor = 0
		while write_sz > 0:
			self._update_chunk()
			to_write = min(write_sz, _CHUNK_SIZE - self.b_offset)
			if self.c is None:
				self.c = FileChunk(
					file=self.f,
					offset=self.c_offset
				)
				self.buf = self.c._buf = bytearray(self.b_offset + to_write)
				self.last_c = self.c_offset
				self.mod_c = True
			chunk_len = len(self.buf)
			if chunk_len < (self.b_offset + to_write):
				extend_sz = self.b_offset + to_write - chunk_len
				self.buf[chunk_len:chunk_len + extend_sz] = (0 for x in range(extend_sz))
			mv = memoryview(self.buf)
			mv[self.b_offset:self.b_offset + to_write] = srcmv[cursor:cursor + to_write]
			self.mod_c = True
			write_sz -= to_write
			cursor += to_write
			self.b_offset += to_write
			if self.b_offset >= _CHUNK_SIZE:
				self.c_offset += 1
				self.b_offset = 0
		after_pos = self.c_offset * _CHUNK_SIZE + self.b_offset
		if after_pos > self.f.size:
			self.f.size = after_pos
		if write_sz <= 0:
			return orig_write_sz
		return (orig_write_sz - write_sz)

	def writelines(self, lines):
		if not (self._mode & _VFS_WRITE):
			raise IOError(errno.EBADF, 'File is not open for writing', self.f)
		raise NotImplementedError

class Tag(Base):
	"""
	Generic object tag.
	"""
	__tablename__ = 'tags_def'
	__table_args__ = (
		Comment('Generic tags'),
		Index('tags_def_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				# no read cap
				'cap_create'    : 'BASE_ADMIN',
				'cap_edit'      : 'BASE_ADMIN',
				'cap_delete'    : 'BASE_ADMIN',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Tags'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('tagid', 'name', 'descr'),
				'grid_hidden'   : ('tagid',),
				'easy_search'   : ('name', 'descr'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' :
					Wizard(
						Step('name', 'descr', title=_('Tag info')),
						title=_('Add new tag')
					)
			}
		}
	)
	id = Column(
		'tagid',
		UInt32(),
		Sequence('tags_def_tagid_seq'),
		Comment('Tag ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Tag name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 2
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Optional tag description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description'),
			'column_flex'   : 3
		}
	)

	def __str__(self):
		return '%s' % str(self.name)

class LogType(Base):
	"""
	Audit log entry type.
	"""
	__tablename__ = 'logs_types'
	__table_args__ = (
		Comment('Log entry types'),
		Index('logs_types_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB', # or leave MyISAM?
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'BASE_ADMIN',
				'cap_create'    : 'BASE_ADMIN',
				'cap_edit'      : 'BASE_ADMIN',
				'cap_delete'    : '__NOPRIV__',

				'show_in_menu'  : 'admin',
				'menu_section'  : _('Logging'),
				'menu_name'     : _('Log Types'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('ltid', 'name'),
				'grid_hidden'   : ('ltid',),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'ltid',
		UInt32(),
		Sequence('logs_types_ltid_seq', start=101, increment=1),
		Comment('Log entry type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Log entry type name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)

	def __str__(self):
		return '%s' % str(self.name)

class LogAction(Base):
	"""
	Audit log action type.
	"""
	__tablename__ = 'logs_actions'
	__table_args__ = (
		Comment('Log actions'),
		Index('logs_actions_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB', # or leave MyISAM?
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : '__NOPRIV__',

				'show_in_menu' : 'admin',
				'menu_section' : _('Logging'),
				'menu_name'    : _('Log Actions'),
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('laid', 'name'),
				'grid_hidden'  : ('laid',),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'laid',
		UInt32(),
		Sequence('logs_actions_laid_seq', start=101, increment=1),
		Comment('Log action ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Log action name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)

	def __str__(self):
		return '%s' % str(self.name)

class LogData(Base):
	"""
	Audit log entry.
	"""
	__tablename__ = 'logs_data'
	__table_args__ = (
		Comment('Actual system log'),
		{
			'mysql_engine'  : 'InnoDB', # or leave MyISAM?
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : '__NOPRIV__',
				'cap_delete'   : '__NOPRIV__',

				'show_in_menu' : 'admin',
				'menu_section' : _('Logging'),
				'menu_name'    : _('Log Data'),
				'default_sort' : ({ 'property': 'ts' ,'direction': 'DESC' },),
				'grid_view'    : ('logid', 'ts', 'login', 'xtype', 'xaction', 'data'),
				'grid_hidden'  : ('logid',),
				'easy_search'  : ('login', 'data'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'logid',
		UInt32(),
		Sequence('logs_data_logid_seq'),
		Comment('Log entry ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('Log entry timestamp'),
		CurrentTimestampDefault(),
		nullable=False,
#		default=zzz,
		info={
			'header_string' : _('Time')
		}
	)
	login = Column(
		Unicode(48),
		Comment('Owner\'s login string'),
		nullable=False,
		info={
			'header_string' : _('Username')
		}
	)
	type_id = Column(
		'type',
		UInt32(),
		ForeignKey('logs_types.ltid', name='logs_data_fk_type', onupdate='CASCADE'),
		Comment('Log entry type'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'filter_type'   : 'list'
		}
	)
	action_id = Column(
		'action',
		UInt32(),
		ForeignKey('logs_actions.laid', name='logs_data_fk_action', onupdate='CASCADE'),
		Comment('Log entry action'),
		nullable=False,
		info={
			'header_string' : _('Action'),
			'filter_type'   : 'list'
		}
	)
	data = Column(
		UnicodeText(),
		Comment('Additional data'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Data'),
			'column_flex'   : 1
		}
	)

	xtype = relationship(
		'LogType',
		innerjoin=True,
		backref='messages'
	)
	xaction = relationship(
		'LogAction',
		innerjoin=True,
		backref='messages'
	)

	def __str__(self):
		return '%s: [%s.%s] %s' % (
			str(self.timestamp),
			str(self.xtype),
			str(self.xaction),
			str(self.data)
		)

class NPSession(Base):
	"""
	NetProfile administrative session.
	"""
	__tablename__ = 'np_sessions'
	__table_args__ = (
		Comment('NetProfile UI sessions'),
		Index('np_sessions_i_uid', 'uid'),
		Index('np_sessions_i_sname', 'sname'),
		Index('np_sessions_i_lastts', 'lastts'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : 'BASE_ADMIN',

				'show_in_menu' : 'admin',
				'menu_name'    : _('UI Sessions'),
				'default_sort' : ({ 'property': 'lastts' ,'direction': 'DESC' },),
				'grid_view'    : ('npsid', 'sname', 'user', 'login', 'startts', 'lastts', 'ipaddr', 'ip6addr'),
				'grid_hidden'  : ('npsid', 'sname'),
				'easy_search'  : ('sname', 'login'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'npsid',
		UInt32(),
		Sequence('np_sessions_npsid_seq'),
		Comment('NP session ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	session_name = Column(
		'sname',
		ASCIIString(255),
		Comment('NP session hash'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='np_sessions_fk_uid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('User'),
			'filter_type'   : 'none',
			'column_flex'   : 1
		}
	)
	login = Column(
		Unicode(48),
		Comment('User login as string'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Username'),
			'column_flex'   : 1
		}
	)
	start_time = Column(
		'startts',
		TIMESTAMP(),
		Comment('Start time'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Start')
		}
#		server_default=text('NULL')
	)
	last_time = Column(
		'lastts',
		TIMESTAMP(),
		Comment('Last seen time'),
		CurrentTimestampDefault(on_update=True),
		nullable=True,
#		default=None,
		info={
			'header_string' : _('Last Update')
		}
	)
	ip_address = Column(
		'ipaddr',
		IPv4Address(),
		Comment('Client IPv4 address'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv4 Address')
		}
	)
	ipv6_address = Column(
		'ip6addr',
		IPv6Address(),
		Comment('Client IPv6 address'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv6 Address'),
			'column_flex'   : 1
		}
	)

	@property
	def end_time(self):
		lastts = self.last_time
		if not lastts:
			return None
		user = self.user
		if not user:
			return None
		secpol = user.effective_policy
		if not secpol:
			return None
		sto = secpol.sess_timeout
		if (not sto) or (sto < 30):
			return None
		et = lastts + dt.timedelta(seconds=sto)
		return et.replace(microsecond=0)

	@classmethod
	def __augment_pg_query__(cls, sess, query, params, req):
		lim = query._limit
		if lim and (lim < 50):
			return query.options(
				joinedload(NPSession.user)
			)
		return query

	def __str__(self):
		return '%s' % str(self.session_name)

	def update_time(self, upt=None):
		if upt is None:
			upt = dt.datetime.now()
		self.last_time = upt

	def check_request(self, req, ts=None):
		user = req.user
		if user != self.user:
			return False
		if not user.enabled:
			return False
		if user.state != UserState.active:
			return False
		secpol = user.effective_policy
		if secpol and (not secpol.check_old_session(req, user, self, ts)):
			return False
		return True

class PasswordHistory(Base):
	"""
	Users' password history entry.
	"""
	__tablename__ = 'users_pwhistory'
	__table_args__ = (
		Comment('Users\' old password history'),
		Index('users_pwhistory_i_uid', 'uid'),
		Index('users_pwhistory_i_ts', 'ts'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
			}
		}
	)
	id = Column(
		'pwhid',
		UInt32(),
		Sequence('users_pwhistory_pwhid_seq'),
		Comment('Password history entry ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='users_pwhistory_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : _('User')
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('Time of change'),
		CurrentTimestampDefault(),
		nullable=False,
#		default=zzz,
		info={
			'header_string' : _('Time')
		}
	)
	password = Column(
		'pass',
		ASCIIString(255),
		Comment('Old password'),
		nullable=False,
		info={
			'header_string' : _('Password')
		}
	)

class GlobalSettingSection(Base):
	"""
	Categories for global settings.
	"""
	__tablename__ = 'np_globalsettings_sections'
	__table_args__ = (
		Comment('NetProfile UI global setting sections'),
		Index('np_globalsettings_sections_u_section', 'npmodid', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'BASE_ADMIN',
				'cap_create'    : 'BASE_ADMIN',
				'cap_edit'      : 'BASE_ADMIN',
				'cap_delete'    : 'BASE_ADMIN',

				'show_in_menu'  : 'admin',
				'menu_section'  : _('Settings'),
				'menu_name'     : _('Global Setting Sections'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('npgssid', 'module', 'name', 'descr'),
				'grid_hidden'   : ('npgssid',),
				'easy_search'   : ('name', 'descr'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new section'))
			}
		}
	)
	id = Column(
		'npgssid',
		UInt32(),
		Sequence('np_globalsettings_sections_npgssid_seq'),
		Comment('Global parameter section ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	module_id = Column(
		'npmodid',
		UInt32(),
		ForeignKey('np_modules.npmodid', name='np_globalsettings_sections_fk_npmodid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('NetProfile module ID'),
		nullable=False,
		info={
			'header_string' : _('Module'),
			'filter_type'   : 'list',
			'column_flex'   : 1
		}
	)
	name = Column(
		Unicode(255),
		Comment('Global parameter section name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Global parameter section description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description'),
			'column_flex'   : 2
		}
	)

	settings = relationship(
		'GlobalSetting',
		backref=backref('section', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		return '%s' % str(self.name)

class UserSettingSection(Base):
	"""
	Categories for per-user settings.
	"""
	__tablename__ = 'np_usersettings_sections'
	__table_args__ = (
		Comment('NetProfile UI user setting sections'),
		Index('np_usersettings_sections_u_section', 'npmodid', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'BASE_ADMIN',
				'cap_create'    : 'BASE_ADMIN',
				'cap_edit'      : 'BASE_ADMIN',
				'cap_delete'    : 'BASE_ADMIN',

				'show_in_menu'  : 'admin',
				'menu_section'  : _('Settings'),
				'menu_name'     : _('User Setting Sections'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('npussid', 'module', 'name', 'descr'),
				'grid_hidden'   : ('npussid',),
				'easy_search'   : ('name', 'descr'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new section'))
			}
		}
	)
	id = Column(
		'npussid',
		UInt32(),
		Sequence('np_usersettings_sections_npussid_seq'),
		Comment('User parameter section ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	module_id = Column(
		'npmodid',
		UInt32(),
		ForeignKey('np_modules.npmodid', name='np_usersettings_sections_fk_npmodid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('NetProfile module ID'),
		nullable=False,
		info={
			'header_string' : _('Module'),
			'filter_type'   : 'list',
			'column_flex'   : 1
		}
	)
	name = Column(
		Unicode(255),
		Comment('User parameter section name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('User parameter section description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description'),
			'column_flex'   : 2
		}
	)

	setting_types = relationship(
		'UserSettingType',
		backref=backref('section', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		return '%s' % str(self.name)

	def get_tree_node(self, req):
		loc = get_localizer(req)
		return {
			'id'      : 'ss' + str(self.id),
			'text'    : loc.translate(_(self.name)),
			'leaf'    : True,
			'iconCls' : 'ico-cog'
		}

class DynamicSetting(object):
	def has_constraint(self, name):
		if self.constraints and (name in self.constraints):
			return True
		return False

	def get_constraint(self, name, default=None):
		if self.constraints and (name in self.constraints):
			return self.constraints[name]
		return default

	def has_option(self, name):
		if self.options and (name in self.options):
			return True
		return False

	def get_option(self, name, default=None):
		if self.options and (name in self.options):
			return self.options[name]
		return default

	def parse_param(self, param):
		if self.type == 'checkbox':
			if isinstance(param, bool):
				return param
			if param.lower() in {'true', '1', 'on', 'yes'}:
				return True
			return False
		cast = self.get_constraint('cast')
		if cast == 'int':
			return int(param)
		if cast == 'float':
			return float(param)
		return param

	def param_to_db(self, param):
		param = self.parse_param(param)
		if self.type == 'checkbox':
			if param:
				return 'true'
			return 'false'
		return str(param)

	def get_field_cfg(self, req):
		cfg = {
			'xtype'       : 'textfield',
			'allowBlank'  : self.get_constraint('nullok', False),
			'name'        : self.name,
			'fieldLabel'  : self.title,
			'description' : self.description
		}
		if self.type == 'text':
			if self.get_constraint('cast') == 'int':
				cfg['xtype'] = 'numberfield'
				cfg['allowDecimals'] = False
				if self.has_constraint('minval'):
					cfg['minValue'] = int(self.get_constraint('minval'))
				if self.has_constraint('maxval'):
					cfg['maxValue'] = int(self.get_constraint('maxval'))
			else:
				if self.has_constraint('minlen'):
					cfg['minLength'] = int(self.get_constraint('minlen'))
				if self.has_constraint('maxlen'):
					cfg['maxLength'] = int(self.get_constraint('maxlen'))
				if self.has_constraint('regex'):
					cfg['regex'] = int(self.get_constraint('regex'))
		if self.type == 'checkbox':
			cfg.update({
				'xtype'          : 'checkbox',
				'inputValue'     : 'true',
				'uncheckedValue' : 'false'
			})
		if self.type == 'select':
			chx = []
			if self.get_constraint('nullok', False):
				chx.append({
					'id'    : '',
					'value' : ''
				})
			opts = self.get_option('options')
			if opts:
				for k, v in opts.items():
					chx.append({
						'id'    : k,
						'value' : v
					})
			cfg.update({
				'xtype'          : 'combobox',
				'format'         : 'string',
				'displayField'   : 'value',
				'hiddenName'     : self.name,
				'valueField'     : 'id',
				'queryMode'      : 'local',
				'editable'       : False,
				'forceSelection' : True,
				'store'          : {
					'xtype'  : 'simplestore',
					'fields' : ('id', 'value'),
					'data'   : chx
				}
			})
		if self.type == 'password':
			cfg['xtype'] = 'passwordfield'
		if self.type == 'textarea':
			cfg['xtype'] = 'textareafield'
		return cfg

class GlobalSetting(Base, DynamicSetting):
	"""
	Global application settings.
	"""
	__tablename__ = 'np_globalsettings_def'
	__table_args__ = (
		Comment('NetProfile UI global settings'),
		Index('np_globalsettings_def_u_name', 'name', unique=True),
		Index('np_globalsettings_def_i_npmodid', 'npmodid'),
		Index('np_globalsettings_def_i_npgssid', 'npgssid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : 'BASE_ADMIN',

				'show_in_menu' : 'admin',
				'menu_section' : _('Settings'),
				'menu_name'    : _('Global Settings'),
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('npglobid', 'module', 'section', 'name', 'title', 'type', 'value', 'default'),
				'grid_hidden'  : ('npglobid',),
				'easy_search'  : ('name', 'title'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'npglobid',
		UInt32(),
		Sequence('np_globalsettings_def_npglobid_seq'),
		Comment('Global parameter ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	section_id = Column(
		'npgssid',
		UInt32(),
		ForeignKey('np_globalsettings_sections.npgssid', name='np_globalsettings_def_fk_npgssid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Global parameter section ID'),
		nullable=False,
		info={
			'header_string' : _('Section'),
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	module_id = Column(
		'npmodid',
		UInt32(),
		ForeignKey('np_modules.npmodid', name='np_globalsettings_def_fk_npmodid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('NetProfile module ID'),
		nullable=False,
		info={
			'header_string' : _('Module'),
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('Global parameter name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 2
		}
	)
	title = Column(
		Unicode(255),
		Comment('Global parameter title'),
		nullable=False,
		info={
			'header_string' : _('Title'),
			'column_flex'   : 3
		}
	)
	type = Column(
		ASCIIString(64),
		Comment('Global parameter type'),
		nullable=False,
		default='text',
		server_default='text',
		info={
			'header_string' : _('Type'),
			'column_flex'   : 1
		}
	)
	value = Column(
		ASCIIString(255),
		Comment('Global parameter current value'),
		nullable=False,
		info={
			'header_string' : _('Value'),
			'column_flex'   : 3
		}
	)
	default = Column(
		ASCIIString(255),
		Comment('Global parameter default value'),
		nullable=True,
		server_default=text('NULL'),
		info={
			'header_string' : _('Default'),
			'column_flex'   : 3
		}
	)
	options = Column(
		'opt',
		PickleType(pickler=HybridPickler),
		Comment('Serialized options array'),
		nullable=True,
		info={
			'header_string' : _('Options')
		}
	)
	dynamic_options = Column(
		'dynopt',
		PickleType(pickler=HybridPickler),
		Comment('Serialized dynamic options array'),
		nullable=True,
		info={
			'header_string' : _('Dynamic Options')
		}
	)
	constraints = Column(
		'constr',
		PickleType(pickler=HybridPickler),
		Comment('Serialized constraints array'),
		nullable=True,
		info={
			'header_string' : _('Constraints')
		}
	)
	client_ok = Column(
		'clientok',
		NPBoolean(),
		Comment('OK to pass to clientside?'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : _('Client-side')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Global parameter description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	@hybrid_property
	def python_value(self):
		return self.parse_param(self.value)

	@python_value.setter
	def python_value_set(self, value):
		self.value = self.param_to_db(value)

	def __str__(self):
		return '%s' % str(self.name)

@cache.cache_on_arguments()
def global_setting(name):
	sess = DBSession()
	try:
		gs = sess.query(GlobalSetting).filter(GlobalSetting.name == name).one()
	except NoResultFound:
		return None
	if gs.value is None:
		return None
	return gs.python_value

def _set_gs(mapper, conn, tgt):
	if tgt.name:
		global_setting.set(tgt.python_value, tgt.name)

def _del_gs(mapper, conn, tgt):
	if tgt.name:
		global_setting.invalidate(tgt.name)

event.listen(GlobalSetting, 'after_delete', _del_gs)
event.listen(GlobalSetting, 'after_insert', _set_gs)
event.listen(GlobalSetting, 'after_update', _set_gs)

class UserSettingType(Base, DynamicSetting):
	"""
	Per-user application setting types.
	"""
	__tablename__ = 'np_usersettings_types'
	__table_args__ = (
		Comment('NetProfile UI user setting types'),
		Index('np_usersettings_types_u_name', 'name', unique=True),
		Index('np_usersettings_types_i_npmodid', 'npmodid'),
		Index('np_usersettings_types_i_npussid', 'npussid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : 'BASE_ADMIN',

				'show_in_menu' : 'admin',
				'menu_section' : _('Settings'),
				'menu_name'    : _('User Setting Types'),
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('npustid', 'module', 'section', 'name', 'title', 'type', 'default', 'clientok'),
				'grid_hidden'  : ('npustid', 'clientok'),
				'easy_search'  : ('name', 'title'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'npustid',
		UInt32(),
		Sequence('np_usersettings_types_npustid_seq'),
		Comment('User parameter type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	section_id = Column(
		'npussid',
		UInt32(),
		ForeignKey('np_usersettings_sections.npussid', name='np_usersettings_types_fk_npussid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User parameter section ID'),
		nullable=False,
		info={
			'header_string' : _('Section'),
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	module_id = Column(
		'npmodid',
		UInt32(),
		ForeignKey('np_modules.npmodid', name='np_usersettings_types_fk_npmodid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('NetProfile module ID'),
		nullable=False,
		info={
			'header_string' : _('Module'),
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('User parameter name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 2
		}
	)
	title = Column(
		Unicode(255),
		Comment('User parameter title'),
		nullable=False,
		info={
			'header_string' : _('Title'),
			'column_flex'   : 3
		}
	)
	type = Column(
		ASCIIString(64),
		Comment('User parameter type'),
		nullable=False,
		default='text',
		server_default='text',
		info={
			'header_string' : _('Type'),
			'column_flex'   : 1
		}
	)
	default = Column(
		ASCIIString(255),
		Comment('User parameter default value'),
		nullable=True,
		server_default=text('NULL'),
		info={
			'header_string' : _('Default'),
			'column_flex'   : 3
		}
	)
	options = Column(
		'opt',
		PickleType(pickler=HybridPickler),
		Comment('Serialized options array'),
		nullable=True,
		info={
			'header_string' : _('Options')
		}
	)
	dynamic_options = Column(
		'dynopt',
		PickleType(pickler=HybridPickler),
		Comment('Serialized dynamic options array'),
		nullable=True,
		info={
			'header_string' : _('Dynamic Options')
		}
	)
	constraints = Column(
		'constr',
		PickleType(pickler=HybridPickler),
		Comment('Serialized constraints array'),
		nullable=True,
		info={
			'header_string' : _('Constraints')
		}
	)
	client_ok = Column(
		'clientok',
		NPBoolean(),
		Comment('OK to pass to clientside?'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : _('Client-side')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Global parameter description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	settings = relationship(
		'UserSetting',
		backref=backref('type', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	@classmethod
	def __augment_pg_query__(cls, sess, query, params, req):
		lim = query._limit
		if lim and (lim < 50):
			return query.options(
				joinedload(UserSettingType.module),
				joinedload(UserSettingType.section)
			)
		return query

	def __str__(self):
		return '%s' % str(self.name)

class UserSetting(Base):
	"""
	Per-user application settings.
	"""

	@classmethod
	def _filter_section(cls, query, value):
		if isinstance(value, int):
			return query.join(UserSettingType, UserSettingSection).filter(UserSettingSection.id == value)
		return query

	__tablename__ = 'np_usersettings_def'
	__table_args__ = (
		Comment('NetProfile UI user settings'),
		Index('np_usersettings_def_u_us', 'uid', 'npustid', unique=True),
		Index('np_usersettings_def_i_npustid', 'npustid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : 'BASE_ADMIN',

				'show_in_menu' : 'admin',
				'menu_section' : _('Settings'),
				'menu_name'    : _('User Settings'),
				'default_sort' : (),
				'grid_view'    : ('npusid', 'user', 'type', 'value'),
				'grid_hidden'  : ('npusid',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple'),
				'extra_search' : (
					SelectFilter('section', _filter_section,
						title=_('Section'),
						data='NetProfile.store.core.UserSettingSection',
						value_field='npussid',
						display_field='name'
					),
				)
			}
		}
	)
	id = Column(
		'npusid',
		UInt32(),
		Sequence('np_usersettings_def_npusid_seq'),
		Comment('User parameter ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='np_usersettings_def_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : _('User'),
			'filter_type'   : 'none',
			'column_flex'   : 1
		}
	)
	type_id = Column(
		'npustid',
		UInt32(),
		ForeignKey('np_usersettings_types.npustid', name='np_usersettings_def_fk_npustid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User parameter type ID'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'filter_type'   : 'list',
			'column_flex'   : 1
		}
	)
	value = Column(
		ASCIIString(255),
		Comment('User parameter current value'),
		nullable=False,
		info={
			'header_string' : _('Value'),
			'column_flex'   : 2
		}
	)

	@property
	def name(self):
		return self.type.name

	@hybrid_property
	def python_value(self):
		return self.type.parse_param(self.value)

	@python_value.setter
	def python_value_set(self, value):
		self.value = self.type.param_to_db(value)

	def __str__(self):
		return '%s.%s' % (
			str(self.user),
			str(self.type)
		)

class DataCache(Base):
	"""
	General purpose per-user keyed data storage.
	"""
	__tablename__ = 'datacache'
	__table_args__ = (
		Comment('Data cache'),
		Index('datacache_u_dc', 'uid', 'dcname', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : 'BASE_ADMIN',

				'show_in_menu' : 'admin',
				'menu_section' : _('Settings'),
				'menu_name'    : _('Data Cache'),
				'default_sort' : (),
				'grid_view'    : ('dcid', 'user', 'dcname'),
				'grid_hidden'  : ('dcid',),
				'form_view'    : ('user', 'dcname', 'dcvalue'),
				'easy_search'  : ('dcname',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'dcid',
		UInt32(),
		Sequence('datacache_dcid_seq'),
		Comment('Data cache ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='datacache_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Data cache owner'),
		nullable=False,
		info={
			'header_string' : _('User'),
			'column_flex'   : 1
		}
	)
	name = Column(
		'dcname',
		ASCIIString(32),
		Comment('Data cache name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	value = Column(
		'dcvalue',
		PickleType(),
		Comment('Data cache value'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Value')
		}
	)

	def __str__(self):
		return '%s' % str(self.name)

_calendar_styles = {
	1  : '#fa7166',
	2  : '#cf2424',
	3  : '#a01a1a',
	4  : '#7e3838',
	5  : '#ca7609',
	6  : '#f88015',
	7  : '#eda12a',
	8  : '#d5b816',
	9  : '#e281ca',
	10 : '#bf53a4',
	11 : '#9d3283',
	12 : '#7a0f60',
	13 : '#542382',
	14 : '#7742a9',
	15 : '#8763ca',
	16 : '#b586e2',
	17 : '#7399f9',
	18 : '#4e79e6',
	19 : '#2951b9',
	20 : '#133897',
	21 : '#1a5173',
	22 : '#1a699c',
	23 : '#3694b7',
	24 : '#64b9d9',
	25 : '#a8c67b',
	26 : '#83ad47',
	27 : '#2e8f0c',
	28 : '#176413',
	29 : '#0f4c30',
	30 : '#386651',
	31 : '#3ea987',
	32 : '#7bc3b5'
}

class CalendarAccess(DeclEnum):
	"""
	Calendar access ENUM.
	"""
	none       = 'N',  _('None'),       10
	read_only  = 'RO', _('Read-only'),  20
	read_write = 'RW', _('Read-write'), 30

class Calendar(Base):
	"""
	Event calendar owned by a user.
	"""
	__tablename__ = 'calendars_def'
	__table_args__ = (
		Comment('User calendars'),
		Index('calendars_def_u_cal', 'uid', 'name', unique=True),
		Index('calendars_def_i_gid', 'gid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'menu_name'     : _('My Calendars'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('calid', 'name', 'user', 'group', 'group_access', 'global_access'),
				'grid_hidden'   : ('calid', 'user'),
				'form_view'     : ('name', 'group', 'group_access', 'global_access', 'style', 'descr'),
				'easy_search'   : ('name', 'descr'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new calendar'))
			}
		}
	)
	id = Column(
		'calid',
		UInt32(),
		Sequence('calendars_def_calid_seq', start=101, increment=1),
		Comment('Calendar ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='calendars_def_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : _('User'),
			'read_only'     : True,
			'filter_type'   : 'none'
		}
	)
	group_id = Column(
		'gid',
		UInt32(),
		ForeignKey('groups.gid', name='calendars_def_fk_gid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Group ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Group'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	name = Column(
		Unicode(255),
		Comment('Calendar name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	group_access = Column(
		CalendarAccess.db_type(),
		Comment('Calendar access rule for owner group'),
		nullable=False,
		default=CalendarAccess.none,
		server_default=CalendarAccess.none,
		info={
			'header_string' : _('Group Access'),
			'column_flex'   : 2
		}
	)
	global_access = Column(
		CalendarAccess.db_type(),
		Comment('Calendar access rule for everyone not in group'),
		nullable=False,
		default=CalendarAccess.none,
		server_default=CalendarAccess.none,
		info={
			'header_string' : _('Global Access'),
			'column_flex'   : 2
		}
	)
	style = Column(
		UInt32(),
		Comment('Calendar style code'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Style'),
			'min_value'     : 0,
			'max_value'     : len(_calendar_styles),
			'editor_xtype'  : 'calendarcolor'
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Calendar description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	events = relationship(
		'Event',
		backref=backref('calendar', innerjoin=True, lazy='joined'),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	imports = relationship(
		'CalendarImport',
		backref=backref('calendar', innerjoin=True, lazy='joined'),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def can_read(self, user):
		if self.user_id == user.id:
			return True
		if (self.group_id is not None) and (self.group_id == user.group.id):
			return (self.group_access != CalendarAccess.none)
		return (self.global_access != CalendarAccess.none)

	def can_write(self, user):
		if self.user_id == user.id:
			return True
		if (self.group_id is not None) and (self.group_id == user.group.id):
			return (self.group_access == CalendarAccess.read_write)
		return (self.global_access == CalendarAccess.read_write)

	def __str__(self):
		return '%s' % str(self.name)

	@classmethod
	def __augment_query__(cls, sess, query, params, req):
		query = query.filter(Calendar.user_id == req.user.id)
		return query

	@classmethod
	def __augment_create__(cls, sess, obj, values, req):
		obj.user_id = req.user.id
		return True

	@classmethod
	def __augment_update__(cls, sess, obj, values, req):
		if obj.user_id == req.user.id:
			return True
		return False

	@classmethod
	def __augment_delete__(cls, sess, obj, values, req):
		if obj.user_id == req.user.id:
			return True
		return False

def _wizfld_import_cal(fld, model, req, **kwargs):
	return {
		'xtype'          : 'combobox',
		'allowBlank'     : False,
		'name'           : 'caldef',
		'format'         : 'string',
		'displayField'   : 'Title',
		'valueField'     : 'CalendarId',
		'hiddenName'     : 'caldef',
		'editable'       : False,
		'forceSelection' : True,
		'store'          : {
			'type'          : 'direct',
			'model'         : 'Extensible.calendar.data.CalendarModel',
			'directFn'      : 'NetProfile.api.Calendar.cal_avail',
			'totalProperty' : 'total',
			'rootProperty'  : 'calendars'
		},
		'fieldLabel'     : _('Calendar'),
		'tpl'            : '<tpl for="."><div class="x-boundlist-item">{Owner}: {Title}</div></tpl>'
	}

def _wizcb_import_cal_submit(wiz, em, step, act, val, req):
	if ('caldef' not in val) or (val['caldef'][:5] != 'user-'):
		raise ValueError
	cal_id = int(val['caldef'][5:])
	sess = DBSession()
	cal = sess.query(Calendar).get(cal_id)
	if (not cal) or (not cal.can_read(req.user)):
		raise ValueError
	imp = CalendarImport()
	imp.user = req.user
	imp.calendar = cal
	name = val.get('name')
	if name:
		imp.name = name
	try:
		style = int(val.get('style'))
		if 0 < style <= len(_calendar_styles):
			imp.style = style
	except (TypeError, ValueError):
		pass
	sess.add(imp)
	return {
		'do'     : 'close',
		'reload' : True
	}

class CalendarImport(Base):
	"""
	Represents a shared calendar which is imported to other user's namespace.
	"""
	__tablename__ = 'calendars_imports'
	__table_args__ = (
		Comment('User calendar imports'),
		Index('calendars_imports_u_import', 'uid', 'calid', unique=True),
		Index('calendars_imports_i_calid', 'calid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'menu_name'     : _('Other Calendars'),
				'default_sort'  : ({ 'property': 'calid' ,'direction': 'ASC' },),
				'grid_view'     : (
					'calimpid',
					'calendar',
					MarkupColumn(
						name='real_name',
						header_string=_('Name'),
						column_flex=3,
						template='{real_name}'
					)
				),
				'grid_hidden'   : ('calimpid',),
				'form_view'     : ('calendar', 'name', 'style'),
				'easy_search'   : ('name',),
				'extra_data'    : ('real_name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : Wizard(
					Step(
						ExtJSWizardField(_wizfld_import_cal),
						'name', 'style',
						id='generic',
						on_submit=_wizcb_import_cal_submit
					),
					title=_('Import a calendar'),
					validator='ImportCalendar'
				)
			}
		}
	)
	id = Column(
		'calimpid',
		UInt32(),
		Sequence('calendars_imports_calimpid_seq'),
		Comment('Calendar import ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='calendars_imports_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : _('User'),
			'read_only'     : True,
			'filter_type'   : 'none'
		}
	)
	calendar_id = Column(
		'calid',
		UInt32(),
		ForeignKey('calendars_def.calid', name='calendars_imports_fk_calid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Calendar ID'),
		nullable=False,
		info={
			'header_string' : _('Calendar'),
			'read_only'     : True,
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	name = Column(
		Unicode(255),
		Comment('Calendar name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	style = Column(
		UInt32(),
		Comment('Calendar style code'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Style'),
			'min_value'     : 0,
			'max_value'     : len(_calendar_styles),
			'editor_xtype'  : 'calendarcolor'
		}
	)

	@property
	def real_name(self):
		if self.name:
			return self.name
		return self.calendar.name

	def __str__(self):
		return '%s' % self.real_name

	@classmethod
	def __augment_query__(cls, sess, query, params, req):
		query = query.filter(CalendarImport.user_id == req.user.id)
		return query

	@classmethod
	def __augment_create__(cls, sess, obj, values, req):
		obj.user_id = req.user.id
		return True

	@classmethod
	def __augment_update__(cls, sess, obj, values, req):
		if obj.user_id == req.user.id:
			return True
		return False

	@classmethod
	def __augment_delete__(cls, sess, obj, values, req):
		if obj.user_id == req.user.id:
			return True
		return False

class Event(Base):
	"""
	User-defined event. Stored in user calendar.
	"""
	__tablename__ = 'calendars_events'
	__table_args__ = (
		Comment('User calendar events'),
		Index('calendars_events_i_calid', 'calid'),
		Index('calendars_events_i_uid', 'uid'), # XXX: add gid?
		Index('calendars_events_i_icaluid', 'icaluid'),
		Index('calendars_events_i_dtstart', 'dtstart'),
		Trigger('before', 'insert', 't_calendars_events_bi'),
		Trigger('before', 'update', 't_calendars_events_bu'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'menu_name'     : _('Events'),
				'default_sort'  : ({ 'property': 'dtstart' ,'direction': 'DESC' },),
				'grid_view'     : ('evid', 'user', 'calendar', 'summary', 'ctime', 'mtime', 'dtstart', 'dtend'),
				'grid_hidden'   : ('evid', 'ctime', 'mtime'),
				'form_view'     : (
					'user', 'calendar', 'summary',
					'dtstart', 'dtend', 'allday',
					'loc', 'url', 'descr',
					'ctime', 'mtime'
				),
				'easy_search'   : ('summary',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'evid',
		UInt32(),
		Sequence('calendars_events_evid_seq'),
		Comment('Event ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	calendar_id = Column(
		'calid',
		UInt32(),
		ForeignKey('calendars_def.calid', name='calendars_events_fk_calid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Calendar ID'),
		nullable=False,
		info={
			'header_string' : _('Calendar'),
			'read_only'     : True,
			'filter_type'   : 'list'
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='calendars_events_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : _('Creator'),
			'read_only'     : True,
			'filter_type'   : 'none'
		}
	)
	summary = Column(
		Unicode(255),
		Comment('Event summary'),
		nullable=False,
		info={
			'header_string' : _('Summary')
		}
	)
	creation_time = Column(
		'ctime',
		TIMESTAMP(),
		Comment('Creation timestamp'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Created')
		}
	)
	modification_time = Column(
		'mtime',
		TIMESTAMP(),
		Comment('Last modification timestamp'),
		CurrentTimestampDefault(on_update=True),
		nullable=False,
#		default=zzz,
		info={
			'header_string' : _('Modified')
		}
	)
	event_start = Column(
		'dtstart',
		TIMESTAMP(),
		Comment('Event start timestamp'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Start')
		}
	)
	event_end = Column(
		'dtend',
		TIMESTAMP(),
		Comment('Event end timestamp'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('End')
		}
	)
	all_day = Column(
		'allday',
		NPBoolean(),
		Comment('Is event all-day?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('All Day')
		}
	)
	icalendar_uid = Column(
		'icaluid',
		Unicode(255),
		Comment('iCalendar UID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('iCal UID')
		}
	)
	location = Column(
		'loc',
		Unicode(255),
		Comment('Event location'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Location')
		}
	)
	url = Column(
		Unicode(255),
		Comment('Event-related URL'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('URL')
		}
	)
	icalendar_data = Column(
		'icaldata',
		LargeBinary(),
		Comment('Original iCalendar data'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('iCal Data')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Event description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	@hybrid_property
	def duration(self):
		return self.event_end - self.event_start

	def __str__(self):
		return '%s' % str(self.summary)

	@classmethod
	def __augment_query__(cls, sess, query, params, req):
		query = query.filter(Event.user_id == req.user.id)
		return query

	@classmethod
	def __augment_create__(cls, sess, obj, values, req):
		obj.user_id = req.user.id
		cal = sess.query(Calendar).get(obj.calendar_id)
		if (not cal) or (not cal.can_write(req.user)):
			return False
		return True

	@classmethod
	def __augment_update__(cls, sess, obj, values, req):
		if obj.user_id == req.user.id:
			return True
		cal = sess.query(Calendar).get(obj.calendar_id)
		if cal and cal.can_write(req.user):
			return True
		return False

	@classmethod
	def __augment_delete__(cls, sess, obj, values, req):
		if obj.user_id == req.user.id:
			return True
		cal = sess.query(Calendar).get(obj.calendar_id)
		if cal and cal.can_write(req.user):
			return True
		return False

HWAddrHexIEEEFunction = SQLFunction(
	'hwaddr_hex_i',
	args=(SQLFunctionArgument('hwbin', BINARY(6)),),
	returns=Unicode(15),
	comment='Convert binary hardware address to IEEE-style string',
	reads_sql=False,
	writes_sql=False
)

HWAddrHexLinuxFunction = SQLFunction(
	'hwaddr_hex_l',
	args=(SQLFunctionArgument('hwbin', BINARY(6)),),
	returns=Unicode(18),
	comment='Convert binary hardware address to Linux-style string',
	reads_sql=False,
	writes_sql=False
)

HWAddrHexWindowsFunction = SQLFunction(
	'hwaddr_hex_w',
	args=(SQLFunctionArgument('hwbin', BINARY(6)),),
	returns=Unicode(18),
	comment='Convert binary hardware address to Windows-style string',
	reads_sql=False,
	writes_sql=False
)

HWAddrUnhexFunction = SQLFunction(
	'hwaddr_unhex',
	args=(SQLFunctionArgument('hwstr', Unicode(255)),),
	returns=BINARY(6),
	comment='Convert various hardware address formats to binary',
	reads_sql=False,
	writes_sql=False
)

