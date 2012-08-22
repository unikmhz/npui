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
	'UserSetting'
]

from sqlalchemy import (
	Boolean,
	CHAR,
	Column,
	DefaultClause,
	FetchedValue,
	ForeignKey,
	Index,
	Integer,
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
	relationship
)

from sqlalchemy.ext.declarative import (
	declarative_base,
	declared_attr
)

from sqlalchemy.ext.associationproxy import (
	association_proxy
)
from sqlalchemy.ext.hybrid import (
	hybrid_property
)
from sqlalchemy.orm.collections import (
	attribute_mapped_collection
)

#from colanderalchemy import (
#	Column,
#	relationship
#)

from netprofile.common.phpserialize import HybridPickler
from netprofile.db.connection import DBSession, Base
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
from netprofile.db.ddl import Comment

import hashlib

def _gen_xcap(cls, k, v):
	"""
	Creator for privilege-related attribute-mapped collections.
	"""
	priv = DBSession.query(Privilege).filter(Privilege.code == k).first()
	if priv is None:
		raise KeyError('Unknown privilege %s' % k)
	return cls(privilege=priv, value=v)

def _gen_xacl(cls, k, v):
	"""
	Creator for ACL-related attribute-mapped collections.
	"""
	priv = DBSession.query(Privilege).filter(Privilege.code == k[0]).first()
	if priv is None:
		raise KeyError('Unknown privilege %s' % k[0])
	return cls(privilege=priv, resource=k[1], value=v)

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
				'menu_name'    : 'Modules',
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
			'header_string' : 'ID'
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('NetProfile module name'),
		nullable=False,
		default=None,
		info={
			'header_string' : 'Name'
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
			'header_string' : 'Version'
		}
	)
	enabled = Column(
		NPBoolean(),
		Comment('Is module enabled?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : 'Enabled'
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

class UserState(DeclEnum):
	"""
	Current user state ENUM.
	"""
	pending = 'P', 'Pending', 10
	active  = 'A', 'Active',  20
	deleted = 'D', 'Deleted', 30

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
				'menu_name'    : 'Users',
				'menu_order'   : 20,
				'default_sort' : (),
				'grid_view'    : ('login', 'name_family', 'name_given', 'group', 'enabled', 'state', 'email'),
				'easy_search'  : ('login', 'name_family'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_user')
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
			'header_string' : 'ID'
		}
	)
	group_id = Column(
		'gid',
		UInt32(),
		ForeignKey('groups.gid', name='users_fk_gid', onupdate='CASCADE'),
		Comment('Group ID'),
		nullable=False,
		info={
			'header_string' : 'Group'
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
			'header_string' : 'Security Policy'
		}
	)
	state = Column(
		UserState.db_type(),
		Comment('User state'),
		nullable=False,
		default=UserState.pending,
		server_default=UserState.pending,
		info={
			'header_string' : 'State'
		}
	)
	login = Column(
		Unicode(48),
		Comment('Login string'),
		nullable=False,
		info={
			'header_string' : 'Username'
		}
	)
	password = Column(
		'pass',
		ASCIIString(255),
		Comment('Some form of password'),
		nullable=False,
		info={
			'header_string' : 'Password',
			'secret_value'  : True
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
			'header_string' : 'A1 Hash',
			'secret_value'  : True
		}
	)
	enabled = Column(
		NPBoolean(),
		Comment('Is logging in enabled?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : 'Enabled'
		}
	)
	name_family = Column(
		Unicode(255),
		Comment('Family name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Family Name'
		}
	)
	name_given = Column(
		Unicode(255),
		Comment('Given name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Given Name'
		}
	)
	name_middle = Column(
		Unicode(255),
		Comment('Middle name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Middle Name'
		}
	)
	title = Column(
		Unicode(255),
		Comment('Title'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Title'
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
			'header_string' : 'Manager'
		}
	)
	email = Column(
		Unicode(64),
		Comment('User\'s e-mail'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'E-mail'
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
			'header_string' : 'IP Address'
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
			'header_string' : 'Random Key'
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
			'header_string' : 'Photo'
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
		'group'
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

	def __str__(self):
		return '%s' % str(self.login)

	@hybrid_property
	def name_full(self):
		return self.name_family + ' ' + self.name_given

	def check_password(self, pwd, hash_con='sha1', salt_len=4):
		if isinstance(pwd, str):
			pwd = pwd.encode()
		salt = self.password[:salt_len].encode()
		orig = self.password[salt_len:]
		ctx = hashlib.new(hash_con)
		ctx.update(salt)
		ctx.update(pwd)
		return ctx.hexdigest() == orig

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
				'menu_name'    : 'Groups',
				'menu_order'   : 30,
				'default_sort' : (),
				'grid_view'    : ('name', 'parent', 'security_policy'),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
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
			'header_string' : 'ID'
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
			'header_string' : 'Parent'
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
			'header_string' : 'Security Policy'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Group Name'),
		nullable=False
	)
	visible = Column(
		NPBoolean(),
		Comment('Is visible in UI?'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : 'Visible'
		}
	)
	assignable = Column(
		NPBoolean(),
		Comment('Can be assigned tasks?'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : 'Assignable'
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
			'header_string' : 'Root Folder'
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
				'menu_name'    : 'Privileges',
				'menu_order'   : 40,
				'default_sort' : (),
				'grid_view'    : ('code', 'name', 'guestvalue', 'hasacls'),
				'easy_search'  : ('code', 'name'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
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
			'header_string' : 'ID'
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
			'header_string' : 'Module'
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
			'header_string' : 'Can be Set'
		}
	)
	code = Column(
		ASCIIString(48),
		Comment('Privilege code'),
		nullable=False,
		info={
			'header_string' : 'Code'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Privilege name'),
		nullable=False,
		info={
			'header_string' : 'Name'
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
			'header_string' : 'Guest Value'
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
			'header_string' : 'Has ACLs'
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
			'header_string' : 'Resource Class'
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
				'header_string' : 'ID'
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
				'header_string' : 'Privilege'
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
				'header_string' : 'Value'
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
				'menu_name'    : 'Group Capabilities',
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
			'header_string' : 'Group'
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
				'menu_name'    : 'Group Capabilities',
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
			'header_string' : 'User'
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
				'header_string' : 'ID'
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
				'header_string' : 'Privilege'
			}
		)

	@declared_attr
	def resource(cls):
		return Column(
			UInt32(),
			Comment('Resource ID'),
			nullable=False,
			info={
				'header_string' : 'Resource'
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
				'header_string' : 'Value'
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
			'header_string' : 'Group'
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
			'header_string' : 'User'
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
			'header_string' : 'ID'
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='users_groups_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : 'User'
		}
	)
	group_id = Column(
		'gid',
		UInt32(),
		ForeignKey('groups.gid', name='users_groups_fk_gid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Group ID'),
		nullable=False,
		info={
			'header_string' : 'Group'
		}
	)

	def __str__(self):
		return '%s' % str(self.group)

class SecurityPolicyOnExpire(DeclEnum):
	"""
	On-password-expire security policy action.
	"""
	none  = 'none',  'No action',          10
	force = 'force', 'Force new password', 20
	drop  = 'drop',  'Drop connection',    30

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
				'menu_name'    : 'Security Policies',
				'menu_order'   : 50,
				'default_sort' : (),
				'grid_view'    : ('name', 'pw_length_min', 'pw_length_max', 'pw_ctype_min', 'pw_ctype_max', 'pw_dict_check', 'pw_hist_check', 'pw_hist_size'),
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
			'header_string' : 'ID'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Security policy name'),
		nullable=False,
		info={
			'header_string' : 'Name'
		}
	)
	pw_length_min = Column(
		UInt16(),
		Comment('Minimum password length'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Min. Password Len.'
		}
	)
	pw_length_max = Column(
		UInt16(),
		Comment('Maximum password length'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Max. Password Len.'
		}
	)
	pw_ctype_min = Column(
		UInt8(),
		Comment('Minimum number of character types in password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Min. Char Types'
		}
	)
	pw_ctype_max = Column(
		UInt8(),
		Comment('Maximum number of character types in password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Max. Char Types'
		}
	)
	pw_dict_check = Column(
		NPBoolean(),
		Comment('Check password against a dictionary?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : 'Dictionary Check'
		}
	)
	pw_dict_name = Column(
		ASCIIString(255),
		Comment('Name of a custom dictionary'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Custom Dictionary'
		}
	)
	pw_hist_check = Column(
		NPBoolean(),
		Comment('Keep a history of old passwords?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : 'Keep History'
		}
	)
	pw_hist_size = Column(
		UInt16(),
		Comment('Old password history size'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'History Size'
		}
	)
	pw_age_min = Column(
		UInt16(),
		Comment('Minimum password age in days'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Min. Password Age'
		}
	)
	pw_age_max = Column(
		UInt16(),
		Comment('Maximum password age in days'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Max. Password Age'
		}
	)
	pw_age_warndays = Column(
		UInt16(),
		Comment('Notify to change password (in days before expiration)'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Notify Days'
		}
	)
	pw_age_warnmail = Column(
		NPBoolean(),
		Comment('Warn about password expiry by e-mail'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : 'Warn by E-mail'
		}
	)
	pw_age_action = Column(
		SecurityPolicyOnExpire.db_type(),
		Comment('Action on expired password'),
		nullable=False,
		default=SecurityPolicyOnExpire.none,
		server_default=SecurityPolicyOnExpire.none,
		info={
			'header_string' : 'On Expire'
		}
	)
	net_whitelist = Column(
		ASCIIString(255),
		Comment('Whitelist of allowed login addresses'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Address Whitelist'
		}
	)
	sess_timeout = Column(
		UInt32(),
		Comment('Session timeout (in seconds)'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Session Timeout'
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
			'header_string' : 'Description'
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

	def __str__(self):
		return '%s' % str(self.name)

class FileFolderAccessRule(DeclEnum):
	private = 'private', 'Owner-only access', 10
	group   = 'group',   'Group-only access', 20
	public  = 'public',  'Public access',     30

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
			'header_string' : 'ID'
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
			'header_string' : 'Parent'
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
			'header_string' : 'User'
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
			'header_string' : 'Group'
		}
	)
	rights = Column(
		UInt32(),
		Comment('Rights bitmask'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : 'Rights'
		}
	)
	access = Column(
		FileFolderAccessRule.db_type(),
		Comment('Folder access rule'),
		nullable=False,
		default=FileFolderAccessRule.public,
		server_default=FileFolderAccessRule.public,
		info={
			'header_string' : 'Access Rule'
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
			'header_string' : 'Created'
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
			'header_string' : 'Modified'
		}
	)
	name = Column(
		ExactUnicode(255),
		Comment('Folder name'),
		nullable=False,
		info={
			'header_string' : 'Name'
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
			'header_string' : 'Description'
		}
	)
	meta = Column(
		PickleType(),
		Comment('Serialized meta-data'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Metadata'
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
			'header_string' : 'ID'
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
			'header_string' : 'Folder'
		}
	)
	filename = Column(
		'fname',
		ExactUnicode(255),
		Comment('File name'),
		nullable=False,
		info={
			'header_string' : 'Filename'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Human-readable file name'),
		nullable=False,
		info={
			'header_string' : 'Name'
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
			'header_string' : 'User'
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
			'header_string' : 'Group'
		}
	)
	rights = Column(
		UInt32(),
		Comment('Rights bitmask'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : 'Rights'
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
			'header_string' : 'Type'
		}
	)
	size = Column(
		UInt32(),
		Comment('File size (in bytes)'),
		nullable=False,
		info={
			'header_string' : 'Size'
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
			'header_string' : 'Created'
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
			'header_string' : 'Modified'
		}
	)
	etag = Column(
		ASCIIString(255),
		Comment('Generated file ETag'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'E-Tag'
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
			'header_string' : 'Read Count'
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
			'header_string' : 'Description'
		}
	)
	meta = Column(
		PickleType(),
		Comment('Serialized meta-data'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Metadata'
		}
	)
	data = deferred(Column(
		LargeBinary(),
		Comment('Actual file data'),
		nullable=False,
		info={
			'header_string' : 'Data'
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
				'cap_menu'     : 'BASE_ADMIN',
				# no read cap
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : 'BASE_ADMIN',

				'show_in_menu' : 'admin',
				'menu_name'    : 'Tags',
				'menu_order'   : 60,
				'default_sort' : (),
				'grid_view'    : ('name', 'descr'),
				'easy_search'  : ('name', 'descr'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
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
			'header_string' : 'ID'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Tag name'),
		nullable=False,
		info={
			'header_string' : 'Name'
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
			'header_string' : 'Description'
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
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : '__NOPRIV__',

				'show_in_menu' : 'admin',
				'menu_section' : 'Logging',
				'menu_name'    : 'Log Types',
				'menu_order'   : 81,
				'default_sort' : (),
				'grid_view'    : ('name',),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
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
			'header_string' : 'ID'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Log entry type name'),
		nullable=False,
		info={
			'header_string' : 'Name'
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
				'menu_section' : 'Logging',
				'menu_name'    : 'Log Actions',
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
			'header_string' : 'ID'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Log action name'),
		nullable=False,
		info={
			'header_string' : 'Name'
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
				'menu_section' : 'Logging',
				'menu_name'    : 'Log Data',
				'menu_order'   : 80,
				'default_sort' : (),
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
			'header_string' : 'ID'
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('Log entry timestamp'),
		nullable=False,
#		default=zzz,
		server_default=func.current_timestamp(),
		info={
			'header_string' : 'Time'
		}
	)
	login = Column(
		Unicode(48),
		Comment('Owner\'s login string'),
		nullable=False,
		info={
			'header_string' : 'Username'
		}
	)
	type_id = Column(
		'type',
		UInt32(),
		ForeignKey('logs_types.ltid', name='logs_data_fk_type', onupdate='CASCADE'),
		Comment('Log entry type'),
		nullable=False,
		info={
			'header_string' : 'Type'
		}
	)
	action_id = Column(
		'action',
		UInt32(),
		ForeignKey('logs_actions.laid', name='logs_data_fk_action', onupdate='CASCADE'),
		Comment('Log entry action'),
		nullable=False,
		info={
			'header_string' : 'Action'
		}
	)
	data = Column(
		UnicodeText(),
		Comment('Additional data'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Data'
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
			str(self.type),
			str(self.action),
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
				'menu_name'    : 'UI Sessions',
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
			'header_string' : 'ID'
		}
	)
	session_name = Column(
		'sname',
		ASCIIString(255),
		Comment('NP session hash'),
		nullable=False,
		info={
			'header_string' : 'Name'
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
			'header_string' : 'User'
		}
	)
	login = Column(
		Unicode(48),
		Comment('User login as string'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Username'
		}
	)
	start_time = Column(
		'startts',
		TIMESTAMP(),
		Comment('Start time'),
		nullable=True,
		default=None,
		info={
			'header_string' : 'Start'
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
			'header_string' : 'Last Update'
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
			'header_string' : 'IPv4 Address'
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
			'header_string' : 'IPv6 Address'
		}
	)

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
			'header_string' : 'ID'
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='users_pwhistory_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : 'User'
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
			'header_string' : 'Time'
		}
	)
	password = Column(
		'pass',
		ASCIIString(255),
		Comment('Old password'),
		nullable=False,
		info={
			'header_string' : 'Password'
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
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : 'BASE_ADMIN',

				'show_in_menu' : 'admin',
				'menu_section' : 'Settings',
				'menu_name'    : 'Global Setting Sections',
				'menu_order'   : 70,
				'default_sort' : (),
				'grid_view'    : ('module', 'name', 'descr'),
				'easy_search'  : ('name', 'descr')
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
			'header_string' : 'ID'
		}
	)
	module_id = Column(
		'npmodid',
		UInt32(),
		ForeignKey('np_modules.npmodid', name='np_globalsettings_sections_fk_npmodid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('NetProfile module ID'),
		nullable=False,
		info={
			'header_string' : 'Module'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Global parameter section name'),
		nullable=False,
		info={
			'header_string' : 'Name'
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
			'header_string' : 'Description'
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
				'cap_menu'     : 'BASE_ADMIN',
				'cap_read'     : 'BASE_ADMIN',
				'cap_create'   : 'BASE_ADMIN',
				'cap_edit'     : 'BASE_ADMIN',
				'cap_delete'   : 'BASE_ADMIN',

				'show_in_menu' : 'admin',
				'menu_section' : 'Settings',
				'menu_name'    : 'User Setting Sections',
				'menu_order'   : 71,
				'default_sort' : (),
				'grid_view'    : ('module', 'name', 'descr'),
				'easy_search'  : ('name', 'descr'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
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
			'header_string' : 'ID'
		}
	)
	module_id = Column(
		'npmodid',
		UInt32(),
		ForeignKey('np_modules.npmodid', name='np_usersettings_sections_fk_npmodid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('NetProfile module ID'),
		nullable=False,
		info={
			'header_string' : 'Module'
		}
	)
	name = Column(
		Unicode(255),
		Comment('User parameter section name'),
		nullable=False,
		info={
			'header_string' : 'Name'
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
			'header_string' : 'Description'
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

class GlobalSetting(Base):
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
				'menu_section' : 'Settings',
				'menu_name'    : 'Global Settings',
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
			'header_string' : 'ID'
		}
	)
	section_id = Column(
		'npgssid',
		UInt32(),
		ForeignKey('np_globalsettings_sections.npgssid', name='np_globalsettings_def_fk_npgssid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Global parameter section ID'),
		nullable=False,
		info={
			'header_string' : 'Section'
		}
	)
	module_id = Column(
		'npmodid',
		UInt32(),
		ForeignKey('np_modules.npmodid', name='np_globalsettings_def_fk_npmodid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('NetProfile module ID'),
		nullable=False,
		info={
			'header_string' : 'Module'
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('Global parameter name'),
		nullable=False,
		info={
			'header_string' : 'Name'
		}
	)
	title = Column(
		Unicode(255),
		Comment('Global parameter title'),
		nullable=False,
		info={
			'header_string' : 'Title'
		}
	)
	type = Column(
		ASCIIString(64),
		Comment('Global parameter type'),
		nullable=False,
		default='text',
		server_default='text',
		info={
			'header_string' : 'Type'
		}
	)
	value = Column(
		ASCIIString(255),
		Comment('Global parameter current value'),
		nullable=False,
		info={
			'header_string' : 'Value'
		}
	)
	default = Column(
		ASCIIString(255),
		Comment('Global parameter default value'),
		nullable=True,
		server_default=text('NULL'),
		info={
			'header_string' : 'Default'
		}
	)
	options = Column(
		'opt',
		PickleType(pickler=HybridPickler),
		Comment('Serialized options array'),
		nullable=True,
		info={
			'header_string' : 'Options'
		}
	)
	dynamic_options = Column(
		'dynopt',
		PickleType(pickler=HybridPickler),
		Comment('Serialized dynamic options array'),
		nullable=True,
		info={
			'header_string' : 'Dynamic Options'
		}
	)
	constraints = Column(
		'constr',
		PickleType(pickler=HybridPickler),
		Comment('Serialized constraints array'),
		nullable=True,
		info={
			'header_string' : 'Constraints'
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
			'header_string' : 'Client-side'
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
			'header_string' : 'Description'
		}
	)

	def __str__(self):
		return '%s' % str(self.name)

class UserSettingType(Base):
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
				'menu_section' : 'Settings',
				'menu_name'    : 'User Setting Types',
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
			'header_string' : 'ID'
		}
	)
	section_id = Column(
		'npussid',
		UInt32(),
		ForeignKey('np_usersettings_sections.npussid', name='np_usersettings_types_fk_npussid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User parameter section ID'),
		nullable=False,
		info={
			'header_string' : 'Section'
		}
	)
	module_id = Column(
		'npmodid',
		UInt32(),
		ForeignKey('np_modules.npmodid', name='np_usersettings_types_fk_npmodid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('NetProfile module ID'),
		nullable=False,
		info={
			'header_string' : 'Module'
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('User parameter name'),
		nullable=False,
		info={
			'header_string' : 'Name'
		}
	)
	title = Column(
		Unicode(255),
		Comment('User parameter title'),
		nullable=False,
		info={
			'header_string' : 'Title'
		}
	)
	type = Column(
		ASCIIString(64),
		Comment('User parameter type'),
		nullable=False,
		default='text',
		server_default='text',
		info={
			'header_string' : 'Type'
		}
	)
	default = Column(
		ASCIIString(255),
		Comment('User parameter default value'),
		nullable=True,
		server_default=text('NULL'),
		info={
			'header_string' : 'Default'
		}
	)
	options = Column(
		'opt',
		PickleType(pickler=HybridPickler),
		Comment('Serialized options array'),
		nullable=True,
		info={
			'header_string' : 'Options'
		}
	)
	dynamic_options = Column(
		'dynopt',
		PickleType(pickler=HybridPickler),
		Comment('Serialized dynamic options array'),
		nullable=True,
		info={
			'header_string' : 'Dynamic Options'
		}
	)
	constraints = Column(
		'constr',
		PickleType(pickler=HybridPickler),
		Comment('Serialized constraints array'),
		nullable=True,
		info={
			'header_string' : 'Constraints'
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
			'header_string' : 'Client-side'
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
			'header_string' : 'Description'
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

class UserSetting(Base):
	"""
	Per-user application settings.
	"""
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
				'menu_section' : 'Settings',
				'menu_name'    : 'User Settings',
				'menu_order'   : 74,
				'default_sort' : (),
				'grid_view'    : ('user', 'type', 'value'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
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
			'header_string' : 'ID'
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='np_usersettings_def_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : 'User'
		}
	)
	type_id = Column(
		'npustid',
		UInt32(),
		ForeignKey('np_usersettings_types.npustid', name='np_usersettings_def_fk_npustid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User parameter type ID'),
		nullable=False,
		info={
			'header_string' : 'Type'
		}
	)
	value = Column(
		ASCIIString(255),
		Comment('User parameter current value'),
		nullable=False,
		info={
			'header_string' : 'Value'
		}
	)

