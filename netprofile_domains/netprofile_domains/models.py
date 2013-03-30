#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
	'DomainServiceType'
]

from sqlalchemy import (
	Column,
	Date,
	ForeignKey,
	Index,
	Sequence,
	Unicode,
	UnicodeText,
	text,
	Text
)

from sqlalchemy.orm import (
	backref,
	relationship
)

from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import Base
from netprofile.db.fields import (
	ASCIIString,
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
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.wizards import SimpleWizard

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
		Index('domains_def_u_domain', 'parentid', 'name', unique=True),
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
				'menu_main'     : True,
				'menu_order'    : 40,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : (
					MarkupColumn(
						name='name',
						header_string=_('Name'),
						template='{__str__}',
						sortable=True
					),
					'parent',
					MarkupColumn(
						name='state',
						header_string=_('State'),
						template="""
<tpl if="enabled">
	<img class="np-inline-img" src="/static/core/img/enabled.png" />
<tpl else>
	<img class="np-inline-img" src="/static/core/img/disabled.png" />
</tpl>
<tpl if="public">
	<img class="np-inline-img" src="/static/core/img/public.png" />
<tpl else>
	<img class="np-inline-img" src="/static/core/img/private.png" />
</tpl>
<tpl if="signed">
	<img class="np-inline-img" src="/static/core/img/lock.png" />
<tpl else>
	<img class="np-inline-img" src="/static/core/img/unlock.png" />
</tpl>
""",
						cell_class='np-nopad',
						column_width=60,
						column_resizable=False
					)
				),
				'form_view'		: (
					'name', 'parent',
					'enabled', 'public', 'signed',
					'soa_refresh', 'soa_retry', 'soa_expire', 'soa_minimum',
					'dkim_name', 'dkim_data',
					'descr'
				),
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
			'header_string' : _('Parent')
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
	signed = Column(
		NPBoolean(),
		Comment('Needs DNSSEC signing?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Signed')
		}
	)
	soa_refresh = Column(
		UInt32(),
		Comment('SOA refresh field'),
		nullable=False,
		default=3600,
		info={
			'header_string' : _('SOA Refresh')
		}
	)
	soa_retry = Column(
		UInt32(),
		Comment('SOA retry field'),
		nullable=False,
		default=300,
		info={
			'header_string' : _('SOA Retry')
		}
	)
	soa_expire = Column(
		UInt32(),
		Comment('SOA expire field'),
		nullable=False,
		default=1814400,
		info={
			'header_string' : _('SOA Expire')
		}
	)
	soa_minimum = Column(
		UInt32(),
		Comment('SOA minimum field'),
		nullable=False,
		default=3600,
		info={
			'header_string' : _('SOA Minimum')
		}
	)
	serial_date = Column(
		Date(),
		Comment('Domain serial date'),
		nullable=False,
		info={
			'header_string' : _('Serial Date'),
			'secret_value'  : True
		}
	)
	serial_revision = Column(
		'serial_rev',
		UInt8(),
		Comment('Domain serial revision'),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Serial Revision'),
			'secret_value'  : True
		}
	)
	dkim_name = Column(
		ASCIIString(255),
		Comment('DKIM public key name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('DKIM Name')
		}
	)
	dkim_data = Column(
		ASCIIText(),
		Comment('DKIM public key body'),
		nullable=True,
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
		backref=backref('parent', remote_side=[id])
	)

	def __str__(self):
		if self.parent:
			return '%s.%s' % (
				str(self.name),
				str(self.parent)
			)
		return '%s' % str(self.name)

class DomainAlias(Base):
	"""
	Domain alias object. Same contents, different name.
	"""
	__tablename__ = 'domains_aliases'
	__table_args__ = (
		Comment('Domains Aliases'),
		Index('domains_aliases_u_da', 'parentid', 'name', unique=True),
		Index('domains_aliases_i_domain', 'domainid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				'cap_read'      : 'DOMAINS_LIST',
				'cap_create'    : 'DOMAINS_CREATE',
				'cap_edit'      : 'DOMAINS_EDIT',
				'cap_delete'    : 'DOMAINS_DELETE',

				'menu_name'     : _('Aliases'),
				'menu_order'    : 40,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : (
					MarkupColumn(
						name='name',
						header_string=_('Name'),
						template='{__str__}',
						sortable=True
					),
					'parent',
					'domain'
				),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new domain alias'))
			}
		}
	)

	id = Column(
		'daid',
		UInt32(),
		Sequence('daid_seq'),
		Comment('Domain alias ID'),
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
			'header_string' : _('Parent')
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
			'header_string' : _('Origin')
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

	domain = relationship(
		'Domain',
		backref='aliases',
		innerjoin=True,
		foreign_keys=domain_id
	)
	parent = relationship(
		'Domain',
		backref='children_aliases',
		foreign_keys=parent_id
	)

	def __str__(self):
		if self.parent:
			return '%s.%s' % (
				str(self.name),
				str(self.parent)
			)
		return '%s' % str(self.name)

class ObjectVisibility(DeclEnum):
	both = 'B', _('Both'), 10
	internal = 'I', _('Internal'), 20
	external = 'E', _('External'), 30

class DomainTXTRecord(Base):
	"""
	Domain TXT record object.
	"""
	__tablename__ = 'domains_txtrr'
	__table_args__ = (
		Comment('Domain TXT records'),
		Index('domains_txtrr_u_txtrr', 'domainid', 'name', unique=True),
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
				'menu_name'     : _('TXT Records'),
				'menu_order'    : 40,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name', 'domain', 'value'),
				'form_view'		: ('name', 'domain', 'ttl', 'vis', 'value'),
				'easy_search'   : ('name', 'value'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new TXT record'))
			}
		}
	)

	id = Column(
		'txtrrid',
		UInt32(),
		Sequence('txtrrid_seq'),
		Comment('Text record ID'),
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
			'header_string' : _('Domain')
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('Text record name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	ttl = Column(
		UInt32(),
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
		Comment('Text record visibility'),
		nullable=False,
		default=ObjectVisibility.both,
		server_default=ObjectVisibility.both,
		info={
			'header_string' : _('Visibility')
		}
	)
	value = Column(
		ASCIITinyText(),
		Comment('Text record value'),
		nullable=False,
		info={
			'header_string' : _('Value')
		}
	)

	domain = relationship(
		'Domain',
		innerjoin=True,
		backref='txt_records'
	)

	def __str__(self):
		if self.domain:
			return '%s.%s' % (
				str(self.name),
				str(self.domain)
			)
		return '%s' % str(self.name)

class DomainServiceType(Base):
	"""
	Domains-to-hosts linkage type.
	"""
	__tablename__ = 'domains_hltypes'
	__table_args__ = (
		Comment('Domains-hosts linkage types'),
		Index('domains_hltypes_u_name', 'name', unique=True),
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
				'menu_name'     : _('Domain Service Types'),
				'menu_order'    : 40,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name', 'unique'),
				'easy_search'   : ('name',),

				'create_wizard' : SimpleWizard(title=_('Add new type'))
			}
		}
	)

	id = Column(
		'hltypeid',
		UInt32(),
		Sequence('hltypeid_seq'),
		Comment('Domains-hosts linkage type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Domains-hosts linkage type name'),
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

