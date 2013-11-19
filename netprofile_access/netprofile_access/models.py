#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Access module - Models
# © Copyright 2013 Alex 'Unik' Unigovsky
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
	'AccessEntity'
]

from sqlalchemy import (
	Column,
	FetchedValue,
	ForeignKey,
	Index,
	Numeric,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	func,
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
	DeclEnum,
	NPBoolean,
	UInt8,
	UInt32,
	UInt64,
	npbool
)
from netprofile.db.ddl import Comment
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.wizards import SimpleWizard
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

from netprofile_entities.models import (
	Entity,
	EntityType
)

_ = TranslationStringFactory('netprofile_access')

EntityType.add_symbol('access', ('access', _('Access'), 50))

class AccessEntity(Entity):
	"""
	Access entity object.
	"""

	DN_ATTR = 'uid'

	__tablename__ = 'entities_access'
	__table_args__ = (
		Comment('Access entities'),
		Index('entities_access_i_stashid', 'stashid'),
		Index('entities_access_i_rateid', 'rateid'),
		Index('entities_access_i_ipaddrid', 'ipaddrid'),
		Index('entities_access_i_ip6addrid', 'ip6addrid'),
		Index('entities_access_i_nextrateid', 'nextrateid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ENTITIES',
				'cap_read'     : 'ENTITIES_LIST',
				'cap_create'   : 'ENTITIES_CREATE',
				'cap_edit'     : 'ENTITIES_EDIT',
				'cap_delete'   : 'ENTITIES_DELETE',

				'show_in_menu' : 'modules',
				'menu_name'    : _('Access Entities'),
				'menu_order'   : 50,
				'menu_parent'  : 'entities',
				'default_sort' : ({ 'property': 'nick' ,'direction': 'ASC' },),
				'grid_view'    : (
					MarkupColumn(
						name='icon',
						header_string='&nbsp;',
						help_text=_('Entity icon'),
						column_width=22,
						column_name=_('Icon'),
						column_resizable=False,
						cell_class='np-nopad',
						template='<img class="np-block-img" src="{grid_icon}" />'
					),
					'nick', 'stash', 'rate'
				),
				'form_view'    : (
					'nick', 'parent', 'state', 'flags',
					'password', 'stash', 'rate', 'next_rate', #'alias_of',
					'ipv4_address', 'ipv6_address',
					'ut_ingress', 'ut_egress', 'u_sec',
					'qpend', 'access_state',
					'pol_ingress', 'pol_egress',
					'bcheck', 'pcheck',
					'descr'
				),
#				'easy_search'  : (),
				'extra_data'    : ('grid_icon',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : EntityType.access
	}
	id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_access_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	password = Column(
		Unicode(255),
		Comment('Cleartext password'),
		nullable=False,
		info={
			'header_string' : _('Password'),
			'secret_value'  : True,
			'editor_xtype'  : 'passwordfield'
		}
	)
	stash_id = Column(
		'stashid',
		UInt32(),
		ForeignKey('stashes_def.stashid', name='entities_access_fk_stashid', onupdate='CASCADE'),
		Comment('Used stash ID'),
		nullable=False,
		info={
			'header_string' : _('Stash'),
			'column_flex'   : 3
		}
	)
	rate_id = Column(
		'rateid',
		UInt32(),
		ForeignKey('rates_def.rateid', name='entities_access_fk_rateid', onupdate='CASCADE'),
		Comment('Used rate ID'),
		nullable=False,
		info={
			'header_string' : _('Rate'),
			'column_flex'   : 2
		}
	)
	alias_of_id = Column(
		'aliasid',
		UInt32(),
		#ForeignKey('entities_access.entityid', name='entities_access_fk_aliasid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Aliased access entity ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Alias Of')
		}
	)
	next_rate_id = Column(
		'nextrateid',
		UInt32(),
		ForeignKey('rates_def.rateid', name='entities_access_fk_nextrateid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Next rate ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Next Rate')
		}
	)
	ipv4_address_id = Column(
		'ipaddrid',
		UInt32(),
		ForeignKey('ipaddr_def.ipaddrid', name='entities_access_fk_ipaddrid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('IPv4 address ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv4 Address')
		}
	)
	ipv6_address_id = Column(
		'ip6addrid',
		UInt64(),
		ForeignKey('ip6addr_def.ip6addrid', name='entities_access_fk_ip6addrid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('IPv6 address ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv6 Address')
		}
	)
	used_traffic_ingress = Column(
		'ut_ingress',
		Numeric(16, 0),
		Comment('Used ingress traffic'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Ingress')
		}
	)
	used_traffic_egress = Column(
		'ut_egress',
		Numeric(16, 0),
		Comment('Used egress traffic'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Egress')
		}
	)
	used_seconds = Column(
		'u_sec',
		UInt32(),
		Comment('Used seconds'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Seconds')
		}
	)
	quota_period_end = Column(
		'qpend',
		TIMESTAMP(),
		Comment('End of quota period'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Ends')
		}
	)
	access_state = Column(
		'state',
		UInt8(),
		Comment('Access code'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Access Code')
		}
	)
	policy_ingress = Column(
		'pol_ingress',
		ASCIIString(255),
		Comment('Ingress traffic policy'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Ingress Policy')
		}
	)
	policy_egress = Column(
		'pol_egress',
		ASCIIString(255),
		Comment('Egress traffic policy'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Egress Policy')
		}
	)
	check_block_state = Column(
		'bcheck',
		NPBoolean(),
		Comment('Check block state'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Check Blocks')
		}
	)
	check_paid_services = Column(
		'pcheck',
		NPBoolean(),
		Comment('Check paid services'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Check Services')
		}
	)

	stash = relationship(
		'Stash',
		innerjoin=True,
		backref='access_entities'
	)
	rate = relationship(
		'Rate',
		innerjoin=True,
		foreign_keys=rate_id,
		backref='access_entities'
	)
	next_rate = relationship(
		'Rate',
		foreign_keys=next_rate_id,
		backref='pending_access_entities'
	)
#	alias_of = relationship(
#		'AccessEntity',
#		foreign_keys=alias_of_id,
#		remote_side=[id],
#		backref='aliases'
#	)
	ipv4_address = relationship(
		'IPv4Address',
		backref='access_entities'
	)
	ipv6_address = relationship(
		'IPv6Address',
		backref='access_entities'
	)

	def grid_icon(self, req):
		return req.static_url('netprofile_access:static/img/access.png')

