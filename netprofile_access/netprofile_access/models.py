#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Access module - Models
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

__all__ = [
	'AccessBlock',
	'AccessEntity',
	'AccessEntityChange',
	'AccessEntityLink',
	'AccessEntityLinkType',
	'PerUserRateModifier',

	'AcctAddProcedure',
	'AcctAuthzProcedure',
	'AcctPollProcedure',
	'AcctRateModsProcedure',
	'AcctRollbackProcedure',
	'CheckAuthFunction',

	'AccessblockExpireEvent',
	'AcctPollEvent'
]

import datetime as dt
from babel.dates import format_datetime

from sqlalchemy import (
	Boolean,
	Column,
	DateTime,
	FetchedValue,
	ForeignKey,
	Index,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	text
)

from sqlalchemy.orm import (
	backref,
	relationship
)
from pyramid.i18n import TranslationStringFactory

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIFixedString,
	ASCIIString,
	DeclEnum,
	ExactUnicode,
	Money,
	NPBoolean,
	Traffic,
	UInt8,
	UInt16,
	UInt32,
	UInt64,
	npbool
)
from netprofile.db.ddl import (
	Comment,
	CurrentTimestampDefault,
	InArgument,
	InOutArgument,
	OutArgument,
	SQLEvent,
	SQLFunction,
	SQLFunctionArgument,
	Trigger
)
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.wizards import (
	SimpleWizard,
	Wizard,
	Step,
	ExternalWizardField
)

from netprofile.ext.data import ExtModel
from netprofile.common.hooks import register_hook
from netprofile.common.crypto import hash_password
from netprofile_entities.models import (
	Entity,
	EntityHistory,
	EntityHistoryPart
)

_ = TranslationStringFactory('netprofile_access')

@register_hook('np.wizard.init.entities.Entity')
def _wizcb_aent_init(wizard, model, req):
	def _wizcb_aent_submit(wiz, em, step, act, val, req):
		sess = DBSession()
		em = ExtModel(AccessEntity)
		obj = AccessEntity()
		# Work around field name clash
		if 'state' in val:
			del val['state']
		em.set_values(obj, val, req, True)
		sess.add(obj)
		return {
			'do'     : 'close',
			'reload' : True
		}

	wizard.steps.append(Step(
		ExternalWizardField('AccessEntity', 'pwd_hashed'),
		ExternalWizardField('AccessEntity', 'stash'),
		ExternalWizardField('AccessEntity', 'rate'),
		id='ent_accessentity1', title=_('Access entity properties'),
		on_prev='generic',
		on_submit=_wizcb_aent_submit
	))

class AccessState(DeclEnum):
	"""
	Enumeration of access entity status codes
	"""
	ok             = 0,  _('OK'),                                  10
	block_auto     = 1,  _('Blocked automatically'),               20
	block_manual   = 2,  _('Blocked manually'),                    30
	block_maxsim   = 3,  _('Blocked after reaching max sessions'), 40
	block_rejected = 4,  _('Rejected'),                            50
	block_inactive = 5,  _('Inactive'),                            60
	error          = 99, _('Error'),                               70

class AccessBlockState(DeclEnum):
	planned = 'planned', _('Planned'), 10
	active  = 'active',  _('Active'),  20
	expired = 'expired', _('Expired'), 30

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
		Index('entities_access_i_aliasid', 'aliasid'),
		Index('entities_access_i_ipaddrid', 'ipaddrid'),
		Index('entities_access_i_ip6addrid', 'ip6addrid'),
		Index('entities_access_i_nextrateid', 'nextrateid'),
		Trigger('before', 'insert', 't_entities_access_bi'),
		Trigger('before', 'update', 't_entities_access_bu'),
		Trigger('after', 'update', 't_entities_access_au'),
		Trigger('after', 'delete', 't_entities_access_ad'),
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
				'menu_parent'  : 'entities',
				'default_sort' : ({'property': 'nick', 'direction': 'ASC'},),
				'grid_view'    : (
					MarkupColumn(
						name='icon',
						header_string='&nbsp;',
						help_text=_('Entity icon'),
						column_width=22,
						column_name=_('Icon'),
						column_resizable=False,
						cell_class='np-nopad',
						template='<tpl if="grid_icon"><img class="np-block-img" src="{grid_icon:encodeURI}" /></tpl>'
					),
					'entityid',
					'nick', 'stash', 'rate'
				),
				'grid_hidden'  : ('entityid',),
				'form_view'    : (
					'nick', 'parent', 'state', 'flags',
					'pwd_hashed', 'stash', 'rate', 'next_rate',  # 'alias_of',
					'ipv4_address', 'ipv6_address',
					'ut_ingress', 'ut_egress', 'u_sec',
					'qpend', 'access_state',
					'pol_ingress', 'pol_egress',
					'bcheck', 'pcheck',
					'descr'
				),
				'easy_search'  : ('nick',),
				'extra_data'    : ('grid_icon',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : Wizard(
					Step(
						'nick', 'parent', 'state',
						'flags', 'descr',
						id='generic', title=_('Generic entity properties'),
					),
					Step(
						'pwd_hashed', 'stash', 'rate',
						id='ent_access1', title=_('Access entity properties'),
					),
					title=_('Add new access entity'), validator='CreateAccessEntity'
				)
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : 5
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
	password_hashed = Column(
		'pwd_hashed',
		ASCIIString(255),
		Comment('Primary storage for hashed password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Password'),
			'secret_value'  : True,
			'editor_xtype'  : 'passwordfield',
			'writer'        : 'change_password',
			'pass_request'  : True
		}
	)
	password_ha1 = Column(
		'pwd_digestha1',
		ASCIIFixedString(32),
		Comment('DIGEST-MD5 A1 hash of access entity password'),
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
	password_ntlm = Column(
		'pwd_ntlm',
		ASCIIFixedString(32),
		Comment('NTLM hash of access entity password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('NTLM Hash'),
			'secret_value'  : True,
			'editor_xtype'  : None
		}
	)
	password_crypt = Column(
		'pwd_crypt',
		ExactUnicode(255),
		Comment('POSIX crypt hash of access entity password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('crypt(3) Hash'),
			'secret_value'  : True,
			'editor_xtype'  : None,
			'ldap_attr'     : 'userPassword',
			'ldap_value'    : 'ldap_password'
		}
	)
	password_plaintext = Column(
		'pwd_plain',
		ExactUnicode(255),
		Comment('Plaintext access entity password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Plaintext Password'),
			'secret_value'  : True,
			'editor_xtype'  : None
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
			'filter_type'   : 'nplist',
			'column_flex'   : 2
		}
	)
	alias_of_id = Column(
		'aliasid',
		UInt32(),
		ForeignKey('entities_access.entityid', name='entities_access_fk_aliasid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Aliased access entity ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Alias Of'),
			'filter_type'   : 'none'
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
			'header_string' : _('Next Rate'),
			'filter_type'   : 'nplist'
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
		Traffic(),
		Comment('Used ingress traffic'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Ingress'),
			'read_only'     : True
		}
	)
	used_traffic_egress = Column(
		'ut_egress',
		Traffic(),
		Comment('Used egress traffic'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Egress'),
			'read_only'     : True
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
			'header_string' : _('Used Seconds'),
			'read_only'     : True
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
			'header_string' : _('Ends'),
			'read_only'     : True
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
			'header_string' : _('Access Code'),
			'choices'       : AccessState,
			'write_cap'     : 'ENTITIES_ACCOUNTSTATE_EDIT'
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
		backref=backref(
			'pending_access_entities',
			passive_deletes=True
		)
	)
	alias_of = relationship(
		'AccessEntity',
		foreign_keys=alias_of_id,
		remote_side=[id],
		backref='aliases'
	)
	ipv4_address = relationship(
		'IPv4Address',
		backref=backref(
			'access_entities',
			passive_deletes=True
		)
	)
	ipv6_address = relationship(
		'IPv6Address',
		backref=backref(
			'access_entities',
			passive_deletes=True
		)
	)
	blocks = relationship(
		'AccessBlock',
		backref=backref('entity', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def data(self, req):
		ret = super(AccessEntity, self).data

		if self.rate:
			ret['rate'] = str(self.rate)
		if self.next_rate:
			ret['nextrate'] = str(self.next_rate)
		if self.quota_period_end:
			ret['qpend'] = format_datetime(self.quota_period_end, locale=req.current_locale)

		ret['accessstate'] = self.access_state_string(req)
		if self.access_state == AccessState.ok.value:
			ret['accessimg'] = 'ok'
		elif self.access_state == AccessState.block_auto.value:
			ret['accessimg'] = 'stop'
		elif self.access_state == AccessState.block_manual.value:
			ret['accessimg'] = 'manual'
		else:
			ret['accessimg'] = 'misc'

		return ret

	def access_state_string(self, req):
		if self.access_state is None:
			return None
		return req.localizer.translate(AccessState.from_string(self.access_state).description)

	def grid_icon(self, req):
		return req.static_url('netprofile_access:static/img/access.png')

	def ldap_password(self, settings):
		if self.password_crypt is None:
			return None
		return '{CRYPT}' + self.password_crypt

	def change_password(self, newpwd, opts, request):
		self.password_hashed = hash_password(self.nick, newpwd, subject='accounts')
		self.password_ntlm = hash_password(self.nick, newpwd, scheme='ntlm', subject='accounts')
		self.password_crypt = hash_password(self.nick, newpwd, scheme='crypt', subject='accounts')
		self.password_plaintext = hash_password(self.nick, newpwd, scheme='plain', subject='accounts')
		if self.nick:
			self.password_ha1 = hash_password(self.nick, newpwd, scheme='digest-ha1', subject='accounts')

class PerUserRateModifier(Base):
	"""
	Per-user rate modifier definition
	"""
	__tablename__ = 'rates_mods_peruser'
	__table_args__ = (
		Comment('Per-user rate modifiers'),
		Index('rates_mods_peruser_u_mapping', 'rmtid', 'entityid', 'rateid', unique=True),
		Index('rates_mods_peruser_i_entityid', 'entityid'),
		Index('rates_mods_peruser_i_rateid', 'rateid'),
		Index('rates_mods_peruser_i_l_ord', 'l_ord'),
		Trigger('before', 'insert', 't_rates_mods_peruser_bi'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES', # FIXME
				'cap_read'      : 'ENTITIES_LIST', # FIXME
				'cap_create'    : 'ENTITIES_EDIT', # FIXME
				'cap_edit'      : 'ENTITIES_EDIT', # FIXME
				'cap_delete'    : 'ENTITIES_EDIT', # FIXME
				'menu_name'     : _('Rate Modifiers'),
				'default_sort'  : ({'property': 'l_ord', 'direction': 'ASC'},),
				'grid_view'     : ('rmid', 'entity', 'rate', 'type', 'enabled', 'l_ord'),
				'grid_hidden'   : ('rmid',),
				'create_wizard' : SimpleWizard(title=_('Add new rate modifier'))
			}
		}
	)
	id = Column(
		'rmid',
		UInt32(),
		Sequence('rates_mods_peruser_rmid_seq'),
		Comment('Rate modifier ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	type_id = Column(
		'rmtid',
		UInt32(),
		Comment('Rate modifier type ID'),
		ForeignKey('rates_mods_types.rmtid', name='rates_mods_peruser_fk_rmtid', ondelete='CASCADE', onupdate='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'filter_type'   : 'nplist',
			'column_flex'   : 1
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		Comment('Access entity ID'),
		ForeignKey('entities_access.entityid', name='rates_mods_peruser_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Account'),
			'filter_type'   : 'none',
			'column_flex'   : 1
		}
	)
	rate_id = Column(
		'rateid',
		UInt32(),
		Comment('Rate ID'),
		ForeignKey('rates_def.rateid', name='rates_mods_peruser_fk_rateid', ondelete='CASCADE', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Rate'),
			'filter_type'   : 'nplist',
			'column_flex'   : 1
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
	enabled = Column(
		NPBoolean(),
		Comment('Is modifier enabled?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Enabled')
		}
	)
	lookup_order = Column(
		'l_ord',
		UInt16(),
		Comment('Lookup order'),
		nullable=False,
		default=1000,
		server_default=text('1000'),
		info={
			'header_string' : _('Lookup Order')
		}
	)

	type = relationship(
		'RateModifierType',
		innerjoin=True,
		backref=backref(
			'per_user_modifiers',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	entity = relationship(
		'AccessEntity',
		innerjoin=True,
		backref=backref(
			'rate_modifiers',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	rate = relationship(
		'Rate',
		backref=backref(
			'per_user_modifiers',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

class AccessBlock(Base):
	"""
	Access block entry object.
	"""
	__tablename__ = 'accessblock_def'
	__table_args__ = (
		Comment('Access entity blocks'),
		Index('accessblock_def_i_entityid', 'entityid'),
		Index('accessblock_def_i_bstate_start', 'bstate', 'startts'),
		Index('accessblock_def_i_startts', 'startts'),
		Trigger('before', 'insert', 't_accessblock_def_bi'),
		Trigger('before', 'update', 't_accessblock_def_bu'),
		Trigger('after', 'insert', 't_accessblock_def_ai'),
		Trigger('after', 'update', 't_accessblock_def_au'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES', # FIXME
				'cap_read'      : 'ENTITIES_LIST', # FIXME
				'cap_create'    : 'ENTITIES_EDIT', # FIXME
				'cap_edit'      : 'ENTITIES_EDIT', # FIXME
				'cap_delete'    : 'ENTITIES_EDIT', # FIXME

				'menu_name'     : _('Access Blocks'),
				'default_sort'  : ({'property': 'startts', 'direction': 'ASC'},),
				'grid_view'     : ('abid', 'entity', 'startts', 'endts', 'bstate'),
				'grid_hidden'   : ('abid',),
				'form_view'     : ('entity', 'startts', 'endts', 'bstate', 'oldstate'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new access block'))
			}
		}
	)
	id = Column(
		'abid',
		UInt32(),
		Sequence('accessblock_def_abid_seq'),
		Comment('Access block ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		Comment('Access entity ID'),
		ForeignKey('entities_access.entityid', name='accessblock_def_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Account'),
			'column_flex'   : 2,
			'filter_type'   : 'none'
		}
	)
	start = Column(
		'startts',
		TIMESTAMP(),
		Comment('Start of block'),
		CurrentTimestampDefault(),
		nullable=False,
		info={
			'header_string' : _('Start'),
			'column_flex'   : 1
		}
	)
	end = Column(
		'endts',
		TIMESTAMP(),
		Comment('End of block'),
		nullable=False,
		info={
			'header_string' : _('End'),
			'column_flex'   : 1
		}
	)
	state = Column(
		'bstate',
		AccessBlockState.db_type(),
		Comment('Block state'),
		nullable=False,
		default=AccessBlockState.expired,
		server_default=AccessBlockState.expired,
		info={
			'header_string' : _('State')
		}
	)
	old_entity_state = Column(
		'oldstate',
		UInt8(),
		Comment('Old entity state'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Access State')
		}
	)

	def __str__(self):
		# FIXME: use datetime range with formats
		return '%s:' % str(self.entity)

class AccessEntityLinkType(Base):
	"""
	Access entity link type object.
	"""
	__tablename__ = 'entities_access_linktypes'
	__table_args__ = (
		Comment('Access entity link types'),
		Index('entities_access_linktypes_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES', # FIXME
				'cap_read'      : 'ENTITIES_LIST', # FIXME
				'cap_create'    : 'ENTITIES_EDIT', # FIXME
				'cap_edit'      : 'ENTITIES_EDIT', # FIXME
				'cap_delete'    : 'ENTITIES_EDIT', # FIXME

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Link Types'),
				'default_sort'  : ({'property': 'name', 'direction': 'ASC'},),
				'grid_view'     : ('ltid', 'name'),
				'grid_hidden'   : ('ltid',),
				'form_view'     : ('name', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new link type'))
			}
		}
	)
	id = Column(
		'ltid',
		UInt32(),
		Sequence('entities_access_linktypes_ltid_seq', start=101, increment=1),
		Comment('Link type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Link type name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Link type description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	def __str__(self):
		return '%s' % self.name

class AccessEntityLink(Base):
	"""
	Access entity link object.
	"""
	__tablename__ = 'entities_access_links'
	__table_args__ = (
		Comment('Access entity links'),
		Index('entities_access_links_i_entityid', 'entityid'),
		Index('entities_access_links_i_ltid', 'ltid'),
		Index('entities_access_links_i_value', 'value'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES', # FIXME
				'cap_read'      : 'ENTITIES_LIST', # FIXME
				'cap_create'    : 'ENTITIES_EDIT', # FIXME
				'cap_edit'      : 'ENTITIES_EDIT', # FIXME
				'cap_delete'    : 'ENTITIES_EDIT', # FIXME

				'menu_name'     : _('Links'),
				'default_sort'  : ({'property': 'ltid', 'direction': 'ASC'},),
				'grid_view'     : ('lid', 'entity', 'type', 'ts', 'value'),
				'grid_hidden'   : ('lid',),
				'easy_search'   : ('value',),
				'create_wizard' : SimpleWizard(title=_('Add new link'))
			}
		}
	)
	id = Column(
		'lid',
		UInt32(),
		Sequence('entities_access_links_lid_seq'),
		Comment('Link ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		Comment('Access entity ID'),
		ForeignKey('entities_access.entityid', name='entities_access_links_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'column_flex'   : 2
		}
	)
	type_id = Column(
		'ltid',
		UInt32(),
		Comment('Link type ID'),
		ForeignKey('entities_access_linktypes.ltid', name='entities_access_links_fk_ltid', ondelete='CASCADE', onupdate='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'column_flex'   : 2
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('Service timestamp'),
		CurrentTimestampDefault(),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Timestamp'),
			'column_flex'   : 1
		}
	)
	value = Column(
		Unicode(255),
		Comment('Link value'),
		nullable=False,
		info={
			'header_string' : _('Value'),
			'column_flex'   : 3
		}
	)

	entity = relationship(
		'AccessEntity',
		innerjoin=True,
		backref=backref(
			'links',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	type = relationship(
		'AccessEntityLinkType',
		innerjoin=True,
		backref=backref(
			'links',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

class AccessEntityChange(Base):
	"""
	Access entity change log object.
	"""
	__tablename__ = 'entities_access_changes'
	__table_args__ = (
		Comment('Changes to access entities'),
		Index('entities_access_changes_i_entityid', 'entityid'),
		Index('entities_access_changes_i_uid', 'uid'),
		Index('entities_access_changes_i_ts', 'ts'),
		Index('entities_access_changes_i_rateid_old', 'rateid_old'),
		Index('entities_access_changes_i_rateid_new', 'rateid_new'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ENTITIES',
				'cap_read'     : 'ENTITIES_LIST',
				'cap_create'   : '__NOPRIV__',
				'cap_edit'     : '__NOPRIV__',
				'cap_delete'   : '__NOPRIV__',

				'menu_name'    : _('Access Entity Changes'),
				'default_sort' : ({'property': 'ts', 'direction': 'DESC'},),
				'grid_view'    : ('aecid', 'entity', 'user', 'ts'),
				'grid_hidden'  : ('aecid',),
				'form_view'    : (
					'entity', 'user', 'ts',
					'pwchanged',
					'state_old', 'state_new',
					'old_rate', 'new_rate',
					'descr'
				),
				'easy_search'  : ('descr',)
			}
		}
	)
	id = Column(
		'aecid',
		UInt64(),
		Sequence('entities_access_changes_aecid_seq'),
		Comment('Access entity change ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		Comment('Access entity ID'),
		ForeignKey('entities_access.entityid', name='entities_access_changes_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'column_flex'   : 2
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		Comment('User ID'),
		ForeignKey('users.uid', name='entities_access_changes_fk_uid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('User'),
			'filter_type'   : 'nplist'
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('Entity change timestamp'),
		CurrentTimestampDefault(),
		nullable=False,
		info={
			'header_string' : _('Time')
		}
	)
	password_changed = Column(
		'pwchanged',
		NPBoolean(),
		Comment('Password was changed'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Changed Password')
		}
	)
	old_access_state = Column(
		'state_old',
		UInt8(),
		Comment('Old access code'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Old Access Code')
		}
	)
	new_access_state = Column(
		'state_new',
		UInt8(),
		Comment('New access code'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('New Access Code')
		}
	)
	old_rate_id = Column(
		'rateid_old',
		UInt32(),
		Comment('Old rate ID'),
		ForeignKey('rates_def.rateid', name='entities_access_changes_fk_rateid_old', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Old Rate'),
			'filter_type'   : 'nplist',
			'column_flex'   : 1
		}
	)
	new_rate_id = Column(
		'rateid_new',
		UInt32(),
		Comment('New rate ID'),
		ForeignKey('rates_def.rateid', name='entities_access_changes_fk_rateid_new', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('New Rate'),
			'filter_type'   : 'nplist',
			'column_flex'   : 1
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Access entity change description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	entity = relationship(
		'AccessEntity',
		innerjoin=True,
		backref=backref(
			'changes',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	user = relationship(
		'User',
		backref=backref(
			'access_entity_changes',
			passive_deletes=True
		)
	)
	old_rate = relationship(
		'Rate',
		lazy='joined',
		foreign_keys=old_rate_id
		# No backref
	)
	new_rate = relationship(
		'Rate',
		lazy='joined',
		foreign_keys=new_rate_id
		# No backref
	)

	def get_entity_history(self, req):
		loc = req.localizer
		eh = EntityHistory(
			self.entity,
			loc.translate(_('Access entity "%s" changed')) % (str(self.entity)),
			self.timestamp,
			None if (self.user is None) else str(self.user)
		)
		if self.password_changed:
			eh.parts.append(EntityHistoryPart('access:password', loc.translate(_('Password was changed'))))
		if self.old_access_state != self.new_access_state:
			recognized = AccessState.values()
			if self.old_access_state in recognized:
				eh.parts.append(EntityHistoryPart('access:state_old', loc.translate(AccessState.from_string(self.old_access_state).description)))
			if self.new_access_state in recognized:
				eh.parts.append(EntityHistoryPart('access:state_new', loc.translate(AccessState.from_string(self.new_access_state).description)))
		if self.old_rate != self.new_rate:
			if self.old_rate:
				eh.parts.append(EntityHistoryPart('access:rate_old', str(self.old_rate)))
			if self.new_rate:
				eh.parts.append(EntityHistoryPart('access:rate_new', str(self.new_rate)))
		if self.description:
			eh.parts.append(EntityHistoryPart('access:comment', self.description))
		return eh

CheckAuthFunction = SQLFunction(
	'check_auth',
	args=(
		SQLFunctionArgument('name', Unicode(255)),
		SQLFunctionArgument('pass', Unicode(255))
	),
	returns=Boolean(),
	comment='Check auth information',
	writes_sql=False
)

AcctAddProcedure = SQLFunction(
	'acct_add',
	args=(
		InArgument('aeid', UInt32()),
		InArgument('username', Unicode(255)),
		InArgument('tin', Traffic()),
		InArgument('teg', Traffic()),
		InArgument('ts', DateTime())
	),
	comment='Add accounting information',
	label='aafunc',
	is_procedure=True
)

AcctAuthzProcedure = SQLFunction(
	'acct_authz',
	args=(
		InArgument('name', Unicode(255)),
	),
	comment='Get authorized account info',
	writes_sql=False,
	label='authzfunc',
	is_procedure=True
)

AcctPollProcedure = SQLFunction(
	'acct_poll',
	args=(
		InArgument('ts', DateTime()),
	),
	comment='Poll accounts for time-based changes',
	is_procedure=True
)

AcctRateModsProcedure = SQLFunction(
	'acct_rate_mods',
	args=(
		InArgument('ts', DateTime()),
		InArgument('rateid', UInt32()),
		InArgument('entityid', UInt32()),
		InOutArgument('oqsum_in', Money()),
		InOutArgument('oqsum_eg', Money()),
		InOutArgument('oqsum_sec', Money()),
		InOutArgument('pol_in', ASCIIString(255)),
		InOutArgument('pol_eg', ASCIIString(255))
	),
	comment='Apply rate modifiers',
	writes_sql=False,
	label='armfunc',
	is_procedure=True
)

AcctRollbackProcedure = SQLFunction(
	'acct_rollback',
	args=(
		InArgument('aeid', UInt32()),
		InArgument('ts', DateTime()),
		InOutArgument('xstashid', UInt32()),
		InArgument('xrateid_old', UInt32()),
		InOutArgument('xrateid_new', UInt32()),
		InOutArgument('uti', Traffic()),
		InOutArgument('ute', Traffic()),
		InOutArgument('xqpend', DateTime()),
		InOutArgument('xstate', UInt8()),
		OutArgument('xdiff', Money())
	),
	comment='Rollback current period for an account',
	label='rbfunc',
	is_procedure=True
)

AccessblockExpireEvent = SQLEvent(
	'ev_accessblock_expire',
	sched_unit='day',
	sched_interval=1,
	comment='Find and mark expired access blocks'
)

AcctPollEvent = SQLEvent(
	'ev_acct_poll',
	sched_unit='day',
	sched_interval=1,
	starts=dt.datetime.combine(dt.date.today(), dt.time(0, 0, 1)),
	comment='Perform passive accounting'
)

