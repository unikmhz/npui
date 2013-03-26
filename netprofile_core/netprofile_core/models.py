#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
	'DataCache'
]

import string
import random
import hashlib
import datetime as dt

from sqlalchemy import (
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
	func,
	text
)

from sqlalchemy.orm import (
	backref,
	deferred,
	joinedload,
	relationship
)

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.collections import attribute_mapped_collection

#from colanderalchemy import (
#	Column,
#	relationship
#)

from netprofile.common import ipaddr
from netprofile.common.phps import HybridPickler
from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIFixedString,
	ASCIIString,
	DeclEnum,
	ExactUnicode,
	IPv4Address,
	IPv6Address,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	npbool
)
from netprofile.ext.wizards import (
	SimpleWizard,
	Step,
	Wizard
)
from netprofile.ext.filters import (
	SelectFilter
)
from netprofile.db.ddl import Comment

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_core')

_DEFAULT_DICT = 'netprofile_core:dicts/np_cmb_rus'

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
				'menu_order'   : 40,
				'default_sort' : (),
				'grid_view'    : ('name', 'curversion', 'enabled'),
				'easy_search'  : ('name',)
			}
		}
	)
	id = Column(
		'npmodid',
		UInt32(),
		Sequence('npmodid_seq'),
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
			'header_string' : _('Name')
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
			'header_string' : _('Version')
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
				'menu_order'   : 20,
				'default_sort' : (),
				'grid_view'    : ('login', 'name_family', 'name_given', 'group', 'enabled', 'state', 'email'),
				'form_view'    : ('login', 'name_family', 'name_given', 'name_middle', 'title', 'group', 'secondary_groups', 'enabled', 'pass', 'security_policy', 'state', 'email', 'manager'),
				'easy_search'  : ('login', 'name_family'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'uid',
		UInt32(),
		Sequence('uid_seq'),
		Comment('User ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
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
			'filter_type'   : 'list'
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
			'header_string' : _('Security Policy')
		}
	)
	state = Column(
		UserState.db_type(),
		Comment('User state'),
		nullable=False,
		default=UserState.pending,
		server_default=UserState.pending,
		info={
			'header_string' : _('State')
		}
	)
	login = Column(
		ExactUnicode(48),
		Comment('Login string'),
		nullable=False,
		info={
			'header_string' : _('Username'),
			'writer'        : 'change_login',
			'pass_request'  : True
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
			'pass_request'  : True
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
			'editor_xtype'  : None
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
			'header_string' : _('Family Name')
		}
	)
	name_given = Column(
		Unicode(255),
		Comment('Given name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Given Name')
		}
	)
	name_middle = Column(
		Unicode(255),
		Comment('Middle name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Middle Name')
		}
	)
	title = Column(
		Unicode(255),
		Comment('Title'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Title')
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
			'header_string' : _('Manager')
		}
	)
	email = Column(
		Unicode(64),
		Comment('User\'s e-mail'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('E-mail')
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

	secondary_groupmap = relationship(
		'UserGroup',
		backref=backref('user', innerjoin=True),
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
		backref='user'
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
		self.mod_pw = False

	def __str__(self):
		return '%s' % str(self.login)

	@hybrid_property
	def name_full(self):
		return self.name_family + ' ' + self.name_given

	def generate_salt(self, salt_len=4, system_rng=True, chars=(string.ascii_lowercase + string.ascii_uppercase + string.digits)):
		if system_rng:
			rng = random.SystemRandom()
		else:
			rng = random
		return ''.join(rng.choice(chars) for i in range(salt_len))

	def generate_a1hash(self, realm):
		ctx = hashlib.md5()
		ctx.update('%s:%s:%s' % (self.login, realm, self.mod_pw))
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
				return
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

	@property
	def flat_privileges(self):
		upriv = self.privileges
		gpriv = self.group.flat_privileges
		for sg in self.secondary_groups:
			if sg == self.group:
				continue
			gpriv.update(sg.flat_privileges)
		gpriv.update(upriv)
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

	def generate_session(self, req, sname):
		now = dt.datetime.now()
		npsess = NPSession(
			user=self,
			login=self.login,
			session_name=sname,
			start_time=now,
			last_time=now
		)
		if 'REMOTE_ADDR' in req.environ:
			try:
				ip = ipaddr.IPAddress(req.environ.get('REMOTE_ADDR'))
				if isinstance(ip, ipaddr.IPv4Address):
					npsess.ip_address = ip
				elif isinstance(ip, ipaddr.IPv6Address):
					npsess.ipv6_address = ip
				print(repr(ip))
			except ValueError:
				pass
		return npsess

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
				'menu_order'   : 30,
				'default_sort' : (),
				'grid_view'    : ('name', 'parent', 'security_policy', 'root_folder'),
				'form_view'    : ('name', 'parent', 'security_policy', 'visible', 'assignable', 'root_folder'),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' :
					Wizard(
						Step('name', 'parent', 'security_policy', title=_('New group data')),
						Step('visible', 'assignable', 'root_folder', title=_('New group details')),
						title=_('Add new group')
					)
			}
		}
	)
	id = Column(
		'gid',
		UInt32(),
		Sequence('gid_seq'),
		Comment('Group ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
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
			'filter_type'   : 'list'
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
			'filter_type'   : 'list'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Group Name'),
		nullable=False,
		info={
			'header_string' : _('Name')
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
			'filter_type'   : 'none'
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
			return self.privileges
		ppriv = self.parent.flat_privileges
		ppriv.update(self.privileges)
		return ppriv

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
				'menu_order'   : 40,
				'default_sort' : (),
				'grid_view'    : ('module', 'code', 'name', 'guestvalue', 'hasacls'),
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
		Sequence('privid_seq'),
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
			'filter_type'   : 'list'
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
			'header_string' : _('Code')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Privilege name'),
		nullable=False,
		info={
			'header_string' : _('Name')
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

class Capability(object):
	"""
	Abstract prototype for privilege assignment object.
	"""
	@declared_attr
	def id(cls):
		return Column(
			'capid',
			UInt32(),
			Sequence('capid_seq'),
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
#				'menu_order'   : 40,
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
#				'menu_order'   : 40,
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
			Sequence('aclid_seq'),
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
		Sequence('ugid_seq'),
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
				'menu_order'   : 50,
				'default_sort' : (),
				'grid_view'    : ('name', 'pw_length_min', 'pw_length_max', 'pw_ctype_min', 'pw_ctype_max', 'pw_dict_check', 'pw_hist_check', 'pw_hist_size'),
				'form_view'    : (
					'name', 'descr',
					'pw_length_min', 'pw_length_max',
					'pw_ctype_min', 'pw_ctype_max',
					'pw_dict_check', 'pw_dict_name',
					'pw_hist_check', 'pw_hist_size',
					'pw_age_min', 'pw_age_max', 'pw_age_warndays', 'pw_age_warnmail', 'pw_age_action',
					'net_whitelist', 'sess_timeout'
				),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'secpolid',
		UInt32(),
		Sequence('secpolid_seq'),
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
			'header_string' : _('Name')
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

	def check_new_password(self, req, user, pwd, ts):
		err = []
		if self.pw_length_min and (len(pwd) < self.pw_length_min):
			err.append('pw_length_min')
		if self.pw_length_max and (len(pwd) > self.pw_length_min):
			err.append('pw_length_max')
		if self.pw_ctypes_min or self.pw_ctypes_max:
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
			if self.pw_ctypes_min and (ct_count < self.pw_ctypes_min):
				err.append('pw_ctypes_min')
			if self.pw_ctypes_max and (ct_count > self.pw_ctypes_max):
				err.append('pw_ctypes_max')
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

	def check_new_session(self, req, user, npsess, ts):
		pass

	def check_old_session(self, req, user, npsess, ts):
		pass

	def __str__(self):
		return '%s' % str(self.name)

class FileFolderAccessRule(DeclEnum):
	private = 'private', _('Owner-only access'), 10
	group   = 'group',   _('Group-only access'), 20
	public  = 'public',  _('Public access'),     30

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
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
			}
		}
	)
	id = Column(
		'ffid',
		UInt32(),
		Sequence('ffid_seq'),
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
			'header_string' : _('User')
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
			'header_string' : _('Group')
		}
	)
	rights = Column(
		UInt32(),
		Comment('Rights bitmask'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Rights')
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
		nullable=False,
#		default=zzz,
		server_default=func.current_timestamp(),
		server_onupdate=func.current_timestamp(),
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
		PickleType(),
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
		backref=backref('parent', remote_side=[id]),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	root_groups = relationship(
		'Group',
		backref='root_folder',
		primaryjoin='FileFolder.id == Group.root_folder_id'
	)

	def __str__(self):
		return '%s' % str(self.name)

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
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
			}
		}
	)
	id = Column(
		'fileid',
		UInt32(),
		Sequence('fileid_seq'),
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
			'header_string' : _('Folder')
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
			'header_string' : _('User')
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
			'header_string' : _('Group')
		}
	)
	rights = Column(
		UInt32(),
		Comment('Rights bitmask'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Rights')
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
			'header_string' : _('Size')
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
		nullable=False,
#		default=zzz,
		server_default=func.current_timestamp(),
		server_onupdate=func.current_timestamp(),
		info={
			'header_string' : _('Modified')
		}
	)
	etag = Column(
		ASCIIString(255),
		Comment('Generated file ETag'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('E-Tag')
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
		PickleType(),
		Comment('Serialized meta-data'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Metadata')
		}
	)
	data = deferred(Column(
		LargeBinary(),
		Comment('Actual file data'),
		nullable=False,
		info={
			'header_string' : _('Data')
		}
	))

	def __str__(self):
		return '%s' % str(self.filename)

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
				'menu_order'    : 60,
				'default_sort'  : (),
				'grid_view'     : ('name', 'descr'),
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
		Sequence('tagid_seq'),
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
			'header_string' : _('Name')
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
			'header_string' : _('Description')
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
				'menu_order'    : 81,
				'default_sort'  : (),
				'grid_view'     : ('name',),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'ltid',
		UInt32(),
		Sequence('ltid_seq'),
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
			'header_string' : _('Name')
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
				'menu_order'   : 82,
				'default_sort' : (),
				'grid_view'    : ('name',),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'laid',
		UInt32(),
		Sequence('laid_seq'),
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
			'header_string' : _('Name')
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
				'menu_order'   : 80,
				'default_sort' : ({ 'property': 'ts' ,'direction': 'DESC' }),
				'grid_view'    : ('ts', 'login', 'xtype', 'xaction', 'data'),
				'easy_search'  : ('login', 'data'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'logid',
		UInt32(),
		Sequence('logid_seq'),
		Comment('Log entry ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(timezone=True),
		Comment('Log entry timestamp'),
		nullable=False,
#		default=zzz,
		server_default=func.current_timestamp(),
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
			'header_string' : _('Data')
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
				'menu_order'   : 90,
				'default_sort' : (),
				'grid_view'    : ('sname', 'user', 'login', 'startts', 'lastts', 'ipaddr', 'ip6addr'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'npsid',
		UInt32(),
		Sequence('npsid_seq'),
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
			'header_string' : _('Name')
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
			'filter_type'   : 'none'
		}
	)
	login = Column(
		Unicode(48),
		Comment('User login as string'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Username')
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
		nullable=True,
#		default=None,
		server_default=func.current_timestamp(),
		server_onupdate=func.current_timestamp(),
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
			'header_string' : _('IPv6 Address')
		}
	)

	@classmethod
	def __augment_pg_query__(cls, sess, query, params):
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
		Sequence('pwhid_seq'),
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
		nullable=False,
#		default=zzz,
		server_default=func.current_timestamp(),
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
				'menu_order'    : 70,
				'default_sort'  : (),
				'grid_view'     : ('module', 'name', 'descr'),
				'easy_search'   : ('name', 'descr'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new section'))
			}
		}
	)
	id = Column(
		'npgssid',
		UInt32(),
		Sequence('npgssid_seq'),
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
			'filter_type'   : 'list'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Global parameter section name'),
		nullable=False,
		info={
			'header_string' : _('Name')
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
			'header_string' : _('Description')
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
				'menu_order'    : 71,
				'default_sort'  : (),
				'grid_view'     : ('module', 'name', 'descr'),
				'easy_search'   : ('name', 'descr'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new section'))
			}
		}
	)
	id = Column(
		'npussid',
		UInt32(),
		Sequence('npussid_seq'),
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
			'filter_type'   : 'list'
		}
	)
	name = Column(
		Unicode(255),
		Comment('User parameter section name'),
		nullable=False,
		info={
			'header_string' : _('Name')
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
			'header_string' : _('Description')
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
			if param.lower() in {'true', '1', 'on'}:
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
			pass
		if self.type == 'select':
			pass
		if self.type == 'password':
			pass
		if self.type == 'textarea':
			pass
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
				'menu_order'   : 72,
				'default_sort' : (),
				'grid_view'    : ('module', 'section', 'name', 'title', 'type', 'value', 'default'),
				'easy_search'  : ('name', 'title'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'npglobid',
		UInt32(),
		Sequence('npglobid_seq'),
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
			'filter_type'   : 'list'
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
			'filter_type'   : 'list'
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('Global parameter name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	title = Column(
		Unicode(255),
		Comment('Global parameter title'),
		nullable=False,
		info={
			'header_string' : _('Title')
		}
	)
	type = Column(
		ASCIIString(64),
		Comment('Global parameter type'),
		nullable=False,
		default='text',
		server_default='text',
		info={
			'header_string' : _('Type')
		}
	)
	value = Column(
		ASCIIString(255),
		Comment('Global parameter current value'),
		nullable=False,
		info={
			'header_string' : _('Value')
		}
	)
	default = Column(
		ASCIIString(255),
		Comment('Global parameter default value'),
		nullable=True,
		server_default=text('NULL'),
		info={
			'header_string' : _('Default')
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

	def __str__(self):
		return '%s' % str(self.name)

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
				'menu_order'   : 73,
				'default_sort' : (),
				'grid_view'    : ('module', 'section', 'name', 'title', 'type', 'default'),
				'easy_search'  : ('name', 'title'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'npustid',
		UInt32(),
		Sequence('npustid_seq'),
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
			'filter_type'   : 'list'
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
			'filter_type'   : 'list'
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('User parameter name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	title = Column(
		Unicode(255),
		Comment('User parameter title'),
		nullable=False,
		info={
			'header_string' : _('Title')
		}
	)
	type = Column(
		ASCIIString(64),
		Comment('User parameter type'),
		nullable=False,
		default='text',
		server_default='text',
		info={
			'header_string' : _('Type')
		}
	)
	default = Column(
		ASCIIString(255),
		Comment('User parameter default value'),
		nullable=True,
		server_default=text('NULL'),
		info={
			'header_string' : _('Default')
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

	def __str__(self):
		return '%s' % str(self.name)

	@classmethod
	def __augment_pg_query__(cls, sess, query, params):
		lim = query._limit
		if lim and (lim < 50):
			return query.options(
				joinedload(UserSettingType.module),
				joinedload(UserSettingType.section)
			)
		return query

class UserSetting(Base):
	"""
	Per-user application settings.
	"""

	@classmethod
	def _filter_section(cls, query, value):
		return query.join(UserSettingType, UserSettingSection).filter(UserSettingSection.id == value)

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
				'menu_order'   : 74,
				'default_sort' : (),
				'grid_view'    : ('user', 'type', 'value'),
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
		Sequence('npusid_seq'),
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
			'filter_type'   : 'none'
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
			'filter_type'   : 'list'
		}
	)
	value = Column(
		ASCIIString(255),
		Comment('User parameter current value'),
		nullable=False,
		info={
			'header_string' : _('Value')
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
				'menu_order'   : 80,
				'default_sort' : (),
				'grid_view'    : ('user', 'dcname'),
				'form_view'    : ('user', 'dcname', 'dcvalue'),
				'easy_search'  : ('dcname',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'dcid',
		UInt32(),
		Sequence('dcid_seq'),
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
			'header_string' : _('User')
		}
	)
	name = Column(
		'dcname',
		ASCIIString(32),
		Comment('Data cache name'),
		nullable=False,
		info={
			'header_string' : _('Name')
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

