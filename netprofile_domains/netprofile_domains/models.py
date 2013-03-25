from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
	'Domain',
	'DomainAlias',
	'DomainTXTRecord',
	'DomainHostLinkageType'
]

from sqlalchemy import (
	Column,
	Date,
	FetchedValue,
	ForeignKey,
	Index,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	func,
	text,
	Text,
	or_
)

from sqlalchemy.orm import (
	backref,
	contains_eager,
	joinedload,
	relationship
)

from netprofile.ext.wizards import (
	SimpleWizard,
	Step,
	Wizard
)
from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIText,
	ASCIITinyText,
	DeclEnum,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	npbool
)
from netprofile.db.ddl import Comment

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_domains')

#TODO: fix one of the model privileges

class Domain(Base):
	"""
	Domain object.
	"""
	__tablename__ = 'domains_def'
	__table_args__ = (
		Comment('Domains'),
		Index('domains_def_u_domain','parentid' ,'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				'cap_read'      : 'DOMAINS_LIST',
				'cap_create'    : 'DOMAINS_CREATE',
				'cap_edit'      : 'DOMAINS_EDIT',
				'cap_delete'    : 'DOMAINS_DELETE',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('Domains'),
				'menu_order'    : 40,
				'default_sort'  : (),
				'grid_view'     : ('name', 'parent'),
				'form_view'		: ('name', 'parent', 'enabled', 'public', 'soa_refresh', 'soa_retry', 'soa_expire', 'soa_minimum', 'dkim_name', 'dkim_data', 'descr'),
				'easy_search'   : ('name', 'descr'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new domain'))
			}
		}
	)

	id = Column(
		'domainid',
		UInt32(),
		Sequence('domainid_seq'),
		Comment('Domain ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	
	parent_id = Column(
		'parentid',
		UInt32(),
		ForeignKey('domains_def.domainid', name='domains_def_fk_parentid', onupdate='CASCADE'),
		Comment('Parent domain ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Parent domain')
		}
	)
	
	name = Column(
		Unicode(255),
		Comment('Domain name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)

	enabled = Column(
		NPBoolean(),
		Comment('Is domain enabled?'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : _('Enabled')
		}
	)

	public = Column(
		NPBoolean(),
		Comment('Is domain visible to outsiders?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Public')
		}
	)

	soa_refresh = Column(
		UInt16(),
		Comment('SOA Refresh Field'),
		nullable=False,
		default=3600,
		info={
			'header_string' : _('SOA Refresh')
		}
	)

	soa_retry = Column(
		UInt16(),
		Comment('SOA Retry Field'),
		nullable=False,
		default=300,
		info={
			'header_string' : _('SOA Retry')
		}
	)

	soa_expire = Column(
		UInt16(),
		Comment('SOA Expire Field'),
		nullable=False,
		default=1814400,
		info={
			'header_string' : _('SOA Expire')
		}
	)

	soa_minimum = Column(
		UInt16(),
		Comment('SOA Minimum Field'),
		nullable=False,
		default=3600,
		info={
			'header_string' : _('SOA Minimum')
		}
	)

	serial_date = Column(
		Date(),
		Comment('Domain Serial Date'),
		nullable=False,
		info={
			'header_string' : _('Serial Date')
		}
	)

	serial_rev = Column(
		UInt8(),
		Comment('Domain Serial Revision'),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Serial Revision')
		}
	)

	dkim_name = Column(
		Unicode(255),
		Comment('DKIM Public Key Name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('DKIM Name')
		}
	)

	dkim_data = Column(
		ASCIIText(),
		Comment('DKIM Public Key Body'),
		nullable=False,
		info={
			'header_string' : _('DKIM Key')
		}
	)

	description = Column(
		'descr',
		UnicodeText(),
		Comment('Domain description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	children = relationship(
		'Domain',
		backref=backref('parent', remote_side=[id]),
	)


	def __str__(self):
		return '%s' % str(self.name)

class DomainAlias(Base):
	"""
	Domaini Alias object.
	"""
	__tablename__ = 'domains_aliases'
	__table_args__ = (
		Comment('Domains Aliases'),
		Index('domains_aliases_u_da','parentid' ,'name', unique=True),
		Index('domains_aliases_i_domain','domainid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				'cap_read'      : 'DOMAINS_LIST',
				'cap_create'    : 'DOMAINS_CREATE',
				'cap_edit'      : 'DOMAINS_EDIT',
				'cap_delete'    : 'DOMAINS_DELETE',

#				'show_in_menu'  : 'modules',
				'menu_name'     : _('Domains aliases'),
				'menu_order'    : 40,
				'default_sort'  : (),
				'grid_view'     : ('name',),
				'form_view'		: ('name', 'parent', 'original'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new alias'))
			}
		}
	)

	id = Column(
		'daid',
		UInt32(),
		Sequence('daid_seq'),
		Comment('Domain Alias ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	
	parent_id = Column(
		'parentid',
		UInt32(),
		ForeignKey('domains_def.domainid', name='domains_aliases_fk_parentid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Parent domain ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Parent domain')
		}
	)
	domain_id = Column(
		'domainid',
		UInt32(),
		ForeignKey('domains_def.domainid', name='domains_aliases_fk_domainid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Original domain ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Original domain')
		}
	)
	
	name = Column(
		Unicode(255),
		Comment('Alias name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)

	original = relationship(
		'Domain',
		backref=backref('aliases',  innerjoin=True),
		foreign_keys=domain_id
	)

	parent = relationship(
		'Domain',
		backref=backref('alias_children'),
		foreign_keys=parent_id
	)

	def __str__(self):
		return '%s' % str(self.name)

class ObjectVisibility(DeclEnum):
	both = 'B', _('Both'), 10
	internal = 'I', _('Internal'), 20
	external = 'E', _('External'), 30

class DomainTXTRecord(Base):
	"""
	Domain TXT Record object.
	"""
	__tablename__ = 'domains_txtrr'
	__table_args__ = (
		Comment('Domain TXT Records'),
		Index('domains_txtrr_u_txtrr','domainid' ,'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				'cap_read'      : 'DOMAINS_LIST',
				'cap_create'    : 'DOMAINS_CREATE',
				'cap_edit'      : 'DOMAINS_EDIT',
				'cap_delete'    : 'DOMAINS_DELETE',

#				'show_in_menu'  : 'modules',
				'menu_name'     : _('Domain TXT records'),
				'menu_order'    : 40,
				'default_sort'  : (),
				'grid_view'     : ('name','value'),
				'form_view'		: ('name', 'domain', 'ttl', 'vis', 'value'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new TXT record'))
			}
		}
	)

	id = Column(
		'txtrrid',
		UInt32(),
		Sequence('txtrrid_seq'),
		Comment('Domain ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	
	domain_id = Column(
		'domainid',
		UInt32(),
		ForeignKey('domains_def.domainid', name='domains_txtrr_fk_domainid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Domain ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Original domain')
		}
	)
	
	name = Column(
		Unicode(255),
		Comment('Record name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)

	ttl = Column(
		UInt16(),
		Comment('Time to live'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('TTL')
		}
	)

	visibility = Column(
		'vis',
		ObjectVisibility.db_type(),
		Comment('Text Record Visibility'),
		nullable=False,
		default=ObjectVisibility.both,
		server_default=ObjectVisibility.both,
		info={
			'header_string' : _('Visibility')
		}
	)

	value = Column(
		ASCIITinyText(),
		Comment('Text Record value'),
		nullable=False,
		info={
			'header_string' : _('Value')
		}
	)

	domain = relationship(
		'Domain',
		backref=backref('txt_records',  innerjoin=True),
		foreign_keys=domain_id
	)

	def __str__(self):
		return '%s' % str(self.name)

class DomainHostLinkageType(Base):
	"""
	Domains-Hosts Linkage Type object.
	"""
	__tablename__ = 'domains_hltypes'
	__table_args__ = (
		Comment('Domains-Hosts Linkage Types'),
		Index('domains_hltypes_u_name','name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				'cap_read'      : 'DOMAINS_LIST',
				'cap_create'    : 'DOMAINS_CREATE',
				'cap_edit'      : 'DOMAINS_EDIT',
				'cap_delete'    : 'DOMAINS_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Domains-Hosts Linkage Types'),
				'menu_order'    : 40,
				'default_sort'  : (),
				'grid_view'     : ('name', 'unique'),
#				'form_view'		: ('name', 'unique'),
				'easy_search'   : ('name',),
#				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new type'))
			}
		}
	)

	id = Column(
		'hltypeid',
		UInt32(),
		Sequence('hltypeid_seq'),
		Comment('Domains-Hosts Linkage Type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)

	name = Column(
		Unicode(255),
		Comment('Domains-Hosts Linkage Type name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)

	unique = Column(
		NPBoolean(),
		Comment('Is unique per domain?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Unique')
		}
	)

	def __str__(self):
		return '%s' % str(self.name)
