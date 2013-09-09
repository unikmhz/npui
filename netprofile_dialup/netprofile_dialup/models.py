#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
	'NAS',
	'IPPool',
	'NASPool'
]

from sqlalchemy import (
	Column,
	ForeignKey,
	Index,
	Sequence,
	Unicode,
	UnicodeText,
	text
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
	IPv6Address,
	UInt32,
	UInt8
)
from netprofile.db.ddl import Comment

from netprofile.ext.wizards import SimpleWizard

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_dialup')


class NAS(Base):
	"""
	NetProfile Network Access Server definition
	"""
	__tablename__ = 'nas_def'
	__table_args__ = (
		Comment('Network access servers'),
		Index('nas_def_u_idstr', 'idstr', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				#'cap_menu'      : 'BASE_NAS',
				#'cap_read'      : 'NAS_LIST',
				#'cap_create'    : 'NAS_CREATE',
				#'cap_edit'      : 'NAS_EDIT',
				#'cap_delete'    : 'NAS_DELETE',
				'menu_name'     : _('Network Access Servers'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'idstr', 'direction': 'ASC' },),
				'grid_view'     : ('idstr',),
				'form_view'     : ('idstr', 'descr'),
				'easy_search'   : ('idstr',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new NAS'))
			}
		}
	)

	id = Column(
		'nasid',
		UInt32(),
		Sequence('nasid_seq'),
		Comment('Network access server ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	id_string = Column(
		'idstr',
		ASCIIString(255),
		Comment('Network access server identification string'),
		nullable=False,
		info={
			'header_string' : _('ID String')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Network access server description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	poolmap = relationship(
		'NASPool',
		backref=backref('nas', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	pools = association_proxy(
		'poolmap',
		'pool',
		creator=lambda v: NASPool(pool=v)
	)

	def __str__(self):
		return '%s' % str(self.id_string)

class IPPool(Base):
	"""
	IP Address Pools
	"""

	__tablename__ = 'ippool_def'
	__table_args__ = (
		Comment('IP address pools'),
		Index('ippool_def_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				#'cap_menu'      : 'BASE_IPPOOL',
				#'cap_read'      : 'IPPOOL_LIST',
				#'cap_create'    : 'IPPOOL_CREATE',
				#'cap_edit'      : 'IPPOOL_EDIT',
				#'cap_delete'    : 'IPPOOL_DELETE',
				'menu_name'     : _('IP Address Pools'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 20,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('name',),
				'form_view'     : ('name', 'ip6prefix', 'ip6plen', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new IP address pool'))
			}
		}
	)

	id = Column(
		'poolid',
		UInt32(),
		Sequence('poolid_seq'),
		Comment('IP address pool ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		'name',
		Unicode(255),
		Comment('IP address pool name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	ipv6_prefix = Column(
		'ip6prefix',
		IPv6Address(),
		Comment('IPv6 prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv6 Prefix')
		}
	)
	ipv6_prefix_length = Column(
		'ip6plen',
		UInt8(),
		Comment('IPv6 prefix length'),
		nullable=False,
		info={
			'header_string' : _('IPv6 Prefix Len.')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('IP address pool description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	nasmap = relationship(
		'NASPool',
		backref=backref('pool', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	nases = association_proxy(
		'nasmap',
		'nas',
		creator=lambda v: NASPool(nas=v)
	)

	def __str__(self):
		return '%s' % str(self.name)

class NASPool(Base):
	"""
	NAS IP Pools
	"""

	__tablename__ = 'nas_pools'
	__table_args__ = (
		Comment('NAS IP pools'),
		Index('nas_pools_u_linkage', 'nasid', 'poolid', unique=True),
		Index('nas_pools_i_poolid', 'poolid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				#'cap_menu'      : 'BASE_NAS',
				#'cap_read'      : 'NAS_LIST',
				#'cap_create'    : 'NAS_CREATE',
				#'cap_edit'      : 'NAS_EDIT',
				#'cap_delete'    : 'NAS_DELETE',
				'menu_name'     : _('NAS IP Pools'),
				'default_sort'  : ({ 'property': 'nasid', 'direction': 'ASC' },),
				'grid_view'     : ('nas', 'pool'),
				'form_view'     : ('nas', 'pool'),
				'create_wizard' : SimpleWizard(title=_('Add new NAS IP pool'))
			}
		}
	)

	id = Column(
		'npid',
		UInt32(),
		Sequence('npid_seq'),
		Comment('NAS IP pool ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	nas_id = Column(
		'nasid',
		UInt32(),
		ForeignKey('nas_def.nasid', name='nas_pools_fk_nasid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Network access server ID'),
		nullable=False,
		info={
			'header_string' : _('NAS')
		}
	)
	pool_id = Column(
		'poolid',
		UInt32(),
		ForeignKey('ippool_def.poolid', name='nas_pools_fk_poolid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('IP address pool ID'),
		nullable=False,
		info={
			'header_string' : _('Pool')
		}
	)

