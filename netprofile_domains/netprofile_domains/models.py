#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Domains module - Models
# © Copyright 2013 Nikita Andriyanov
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
	'Domain',
	'DomainAlias',
	'DomainTXTRecord',
	'DomainServiceType',

	'DomainGetFullFunction',

	'DomainsBaseView',
	'DomainsEnabledView',
	'DomainsPublicView',
	'DomainsSignedView'
]

from sqlalchemy import (
	Column,
	Date,
	ForeignKey,
	Index,
	Sequence,
	Unicode,
	UnicodeText,
	literal_column,
	text,
	Text
)

from sqlalchemy.orm import (
	backref,
	relationship
)

from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import (
	Base,
	DBSession
)
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
from netprofile.db.ddl import (
	Comment,
	SQLFunction,
	SQLFunctionArgument,
	Trigger,
	View
)
from netprofile.tpl import TemplateObject
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.wizards import (
	SimpleWizard,
	Step,
	Wizard
)

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
		Trigger('after', 'insert', 't_domains_def_ai'),
		Trigger('after', 'update', 't_domains_def_au'),
		Trigger('after', 'delete', 't_domains_def_ad'),
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
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : (
					'domainid',
					MarkupColumn(
						name='name',
						header_string=_('Name'),
						template='{__str__}',
						column_flex=1,
						sortable=True
					),
					'parent',
					MarkupColumn(
						name='state',
						header_string=_('State'),
						template=TemplateObject('netprofile_domains:templates/domain_icons.mak'),
						cell_class='np-nopad',
						column_width=60,
						column_resizable=False
					)
				),
				'grid_hidden'   : ('domainid',),
				'form_view'		: (
					'name', 'parent',
					'enabled', 'public', 'signed',
					'soa_refresh', 'soa_retry', 'soa_expire', 'soa_minimum',
					'spf_gen', 'spf_rule', 'spf_errmsg',
					'dkim_name', 'dkim_data', 'dkim_test', 'dkim_subdomains', 'dkim_strict',
					'dmarc_trailer',
					'descr'
				),
				'easy_search'   : ('name', 'descr'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : Wizard(
					Step('name', 'parent', 'enabled', 'public', 'signed', 'descr', title=_('Domain info')),
					Step('soa_refresh', 'soa_retry', 'soa_expire', 'soa_minimum', 'dkim_name', 'dkim_data', title=_('DNS options')),
					title=_('Add new domain')
				)
			}
		}
	)

	id = Column(
		'domainid',
		UInt32(),
		Sequence('domains_def_domainid_seq'),
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
			'header_string' : _('Parent'),
			'column_flex'   : 1
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
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('DKIM Key')
		}
	)
	dkim_test = Column(
		NPBoolean(),
		Comment('Use DKIM in test mode'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('DKIM Test')
		}
	)
	dkim_subdomains = Column(
		NPBoolean(),
		Comment('Propagate DKIM rules to subdomains'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('DKIM in Subdomains')
		}
	)
	dkim_strict = Column(
		NPBoolean(),
		Comment('Use DKIM strict check and discard'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('DKIM Strict')
		}
	)
	spf_generate = Column(
		'spf_gen',
		NPBoolean(),
		Comment('Generate SPF record'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : _('Use SPF')
		}
	)
	spf_rule = Column(
		ASCIIText(),
		Comment('Custom SPF rule'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Custom SPF Rule')
		}
	)
	spf_error_message = Column(
		'spf_errmsg',
		UnicodeText(),
		Comment('Custom SPF error explanation string'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('SPF Error')
		}
	)
	dmarc_trailer = Column(
		ASCIIString(255),
		Comment('DMARC record trailer'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('DMARC Trailer')
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

	@property
	def serial(self):
		if not self.serial_date:
			return str(self.serial_revision % 100)
		return '%s%02d' % (
			self.serial_date.strftime('%Y%m%d'),
			(self.serial_revision % 100)
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
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : (
					'daid',
					MarkupColumn(
						name='name',
						header_string=_('Name'),
						template='{__str__}',
						column_flex=1,
						sortable=True
					),
					'parent',
					'domain'
				),
				'grid_hidden'   : ('daid',),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new domain alias'))
			}
		}
	)

	id = Column(
		'daid',
		UInt32(),
		Sequence('domains_aliases_daid_seq'),
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
			'header_string' : _('Parent'),
			'column_flex'   : 1
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
		Trigger('before', 'insert', 't_domains_txtrr_bi'),
		Trigger('before', 'update', 't_domains_txtrr_bu'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				'cap_read'      : 'DOMAINS_LIST',
				'cap_create'    : 'DOMAINS_EDIT',
				'cap_edit'      : 'DOMAINS_EDIT',
				'cap_delete'    : 'DOMAINS_EDIT',
				'menu_name'     : _('TXT Records'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('txtrrid', 'name', 'domain', 'value'),
				'grid_hidden'   : ('txtrrid',),
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
		Sequence('domains_txtrr_txtrrid_seq'),
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
			'header_string' : _('Domain'),
			'column_flex'   : 1
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('Text record name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
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
			'header_string' : _('Value'),
			'column_flex'   : 1
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
				'cap_create'    : 'DOMAINS_SERVICETYPES_CREATE',
				'cap_edit'      : 'DOMAINS_SERVICETYPES_EDIT',
				'cap_delete'    : 'DOMAINS_SERVICETYPES_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Domain Service Types'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('hltypeid', 'name', 'unique'),
				'grid_hidden'   : ('hltypeid',),
				'easy_search'   : ('name',),

				'create_wizard' : SimpleWizard(title=_('Add new type'))
			}
		}
	)

	id = Column(
		'hltypeid',
		UInt32(),
		Sequence('domains_hltypes_hltypeid_seq', start=101, increment=1),
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
			'header_string' : _('Name'),
			'column_flex'   : 1
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

DomainGetFullFunction = SQLFunction(
	'domain_get_full',
	args=(SQLFunctionArgument('did', UInt32()),),
	returns=Unicode(255),
	comment='Get fully qualified name of a domain',
	writes_sql=False
)

DomainsBaseView = View(
	'domains_base',
	DBSession.query(
		Domain.id.label('domainid'),
		literal_column('NULL').label('parentid'),
		Domain.name.label('name'),
		Domain.enabled.label('enabled'),
		Domain.public.label('public'),
		Domain.signed.label('signed'),
		Domain.soa_refresh.label('soa_refresh'),
		Domain.soa_retry.label('soa_retry'),
		Domain.soa_expire.label('soa_expire'),
		Domain.soa_minimum.label('soa_minimum'),
		Domain.serial_date.label('serial_date'),
		Domain.serial_revision.label('serial_rev'),
		Domain.dkim_name.label('dkim_name'),
		Domain.dkim_data.label('dkim_data'),
		Domain.description.label('descr')
	).select_from(Domain).filter(Domain.parent_id == None),
	check_option='CASCADED'
)

DomainsEnabledView = View(
	'domains_enabled',
	DBSession.query(
		Domain.id.label('domainid'),
		Domain.parent_id.label('parentid'),
		Domain.name.label('name'),
		Domain.enabled.label('enabled'),
		Domain.public.label('public'),
		Domain.signed.label('signed'),
		Domain.soa_refresh.label('soa_refresh'),
		Domain.soa_retry.label('soa_retry'),
		Domain.soa_expire.label('soa_expire'),
		Domain.soa_minimum.label('soa_minimum'),
		Domain.serial_date.label('serial_date'),
		Domain.serial_revision.label('serial_rev'),
		Domain.dkim_name.label('dkim_name'),
		Domain.dkim_data.label('dkim_data'),
		Domain.description.label('descr')
	).select_from(Domain).filter(Domain.enabled == True),
	check_option='CASCADED'
)

DomainsPublicView = View(
	'domains_public',
	DBSession.query(
		Domain.id.label('domainid'),
		Domain.parent_id.label('parentid'),
		Domain.name.label('name'),
		Domain.enabled.label('enabled'),
		Domain.public.label('public'),
		Domain.signed.label('signed'),
		Domain.soa_refresh.label('soa_refresh'),
		Domain.soa_retry.label('soa_retry'),
		Domain.soa_expire.label('soa_expire'),
		Domain.soa_minimum.label('soa_minimum'),
		Domain.serial_date.label('serial_date'),
		Domain.serial_revision.label('serial_rev'),
		Domain.dkim_name.label('dkim_name'),
		Domain.dkim_data.label('dkim_data'),
		Domain.description.label('descr')
	).select_from(Domain).filter(Domain.public == True),
	check_option='CASCADED'
)

DomainsSignedView = View(
	'domains_signed',
	DBSession.query(
		Domain.id.label('domainid'),
		Domain.parent_id.label('parentid'),
		Domain.name.label('name'),
		Domain.enabled.label('enabled'),
		Domain.public.label('public'),
		Domain.signed.label('signed'),
		Domain.soa_refresh.label('soa_refresh'),
		Domain.soa_retry.label('soa_retry'),
		Domain.soa_expire.label('soa_expire'),
		Domain.soa_minimum.label('soa_minimum'),
		Domain.serial_date.label('serial_date'),
		Domain.serial_revision.label('serial_rev'),
		Domain.dkim_name.label('dkim_name'),
		Domain.dkim_data.label('dkim_data'),
		Domain.description.label('descr')
	).select_from(Domain).filter(Domain.signed == True),
	check_option='CASCADED'
)

