#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
    "OperationClass",
    "IOOperationType",
    "StashOperationType",
    "Stash",
    "StashIOType",
    "StashIO",
    "StashOperation",
    ]

from sqlalchemy import (
    Column,
    DateTime,
    Date,
    FetchedValue,
    ForeignKey,
    Index,
    Numeric,
    Sequence,
    TIMESTAMP,
    Unicode,
    UnicodeText,
    func,
    text,
    or_
    )

from sqlalchemy.orm import (
    backref,
    contains_eager,
    joinedload,
    relationship,
    validates,
    )

from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy.ext.hybrid import hybrid_property

from netprofile.db.connection import (
    Base,
    DBSession
    )
from netprofile.db.fields import (
    ASCIIString,
    DeclEnum,
    NPBoolean,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
    npbool,
    )
from netprofile.db.ddl import Comment
from netprofile.db.util import (
    populate_related,
    populate_related_list
    )
from netprofile.tpl import TemplateObject
from netprofile.ext.data import (
    ExtModel,
    _name_to_class
    )
from netprofile.ext.columns import (
    HybridColumn,
    MarkupColumn
    )

from netprofile.ext.wizards import (
    ExternalWizardField,
	SimpleWizard,
	Step,
	Wizard
        )
from pyramid.threadlocal import get_current_request
from pyramid.i18n import (
    TranslationStringFactory,
	get_localizer
        )

from mako.template import Template

_ = TranslationStringFactory('netprofile_stashes')


class OperationClass(DeclEnum):
    """
    Stash I/O Class definition
    """
    system = 'system', _('System'),   10
    user = 'user', _('User'), 20


class IOOperationType(DeclEnum):
    """
    Stash I/O Type definition
    """
    inout = 'inout', _('InOut'),   10
    incoming = 'in', _('Incoming'), 20
    outcoming = 'out', _('Outcoming'), 30
    

class StashOperationType(DeclEnum):
    """
    Stash Operation Type definition
    """
    #
    #add/sub - добавление или снятие со счёта
    #qin - входящий трафик в пределах квоты
    #oqin - за пределами квоты (превышение)
    #min - mixed (частично в квоте, частично превышение)
    #eg - аналогично, только для исходящего
    #cash - деньги в кассе
    sub_qin_qeg = 'sub_qin_qeg', _('Subtract quota ingress quota egress'),   10    #Subtract quota ingress quota egress
    sub_min_qeg = 'sub_min_qeg', _('Subtract mixed egress quota egress'), 20      #Subtract mixed egress quota egress
    sub_oqin_qeg = 'sub_oqin_qeg', _('Subtract out of quota ingress quota egress'), 30   #Subtract out of quota ingress quota egress
    sub_qin_meg = 'sub_qin_meg', _('Subtract quota ingress mixed egress'), 40      #Subtract quota ingress mixed egress
    sub_qin_oqeg = 'sub_qin_oqeg', _('Subtract quota ingress out of quota egress'), 50   #Subtract quota ingress out of quota egress
    sub_min_meg = 'sub_min_meg', _('Subtract mixed ingress mixed egress'), 60      #Subtract mixed ingress mixed egress
    sub_oqin_meg = 'sub_oqin_meg', _('Subtract out of quota ingress mixed egress'), 70   #Subtract out of quota ingress mixed egress
    sub_min_oqeg = 'sub_min_oqeg', _('Subtract mixed ingress mixed egress'), 80   #Subtract mixed ingress mixed egress
    sub_oqin_oqeg = 'sub_oqin_oqeg', _('Subtract out of quota ingres out of quota egres'), 90#Subtract out of quota ingres out of quota egres
    add_cash = 'add_cash', _('Add cash'), 100              
    add_auto = 'add_auto', _('Add auto'), 110              
    oper = 'oper', _('Operator'), 120                      
    rollback = 'rollback', _('Rollback'), 130              


class Stash(Base):
    """
    Netprofile Stashes of Money Class Definition
    """
    __tablename__ = 'stashes_def'
    __table_args__ = (
        Comment('Stashes of Money'),
        Index('stashes_def_i_entityid', 'entityid'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'menu_name'    : _('Stashes'),
                'show_in_menu'  : 'modules',
                'menu_order'    : 80,
                'default_sort' : ({ 'property': 'name', 'direction': 'ASC' },),
                'grid_view' : ('entity', 'name', 'amount', 'credit'),
                'form_view' : ('entity', 'name', 'amount', 'credit', 'alltime_max', 'alltime_min'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new stash'))
                }
            }
        )
    id = Column(
        'stashid',
        UInt32(10),
        Sequence('stashid_seq'),
        Comment('Stash ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    entityid = Column(
        'entityid',
        UInt32(10),
        Comment('Owner Entity ID'),
        ForeignKey('entities_def.entityid', name='stashes_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Entity')
            }
        )
    name  = Column(
        'name',
        Unicode(255),
        Comment('Stash Name'),
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    amount = Column(
        'amount',
        Numeric(20, 8),
        Comment('Funds in Stash'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Funds')
            }
        )
    credit = Column(
        'credit',
        Numeric(20, 8),
        Comment('Stash Credit'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Credit')
            }
        )
    alltime_max = Column(
        'alltime_max',
        Numeric(20, 8),
        Comment('All-Time Maximum Funds'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Maximum Funds')
            }
        )
    alltime_min = Column(
        'alltime_min',
        Numeric(20, 8),
        Comment('All-Time Minimum Funds'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Minimum Funds')
            }
        )

    entity = relationship('Entity', backref=backref('stashentity', innerjoin=True))

    def __str__(self):
        return "{0}, {1}".format(self.entity, self.name)


class StashIOType(Base):
    """
    Netprofile Stashes Input/Output Operation Type definition
    """
    __tablename__ = 'stashes_io_types'
    __table_args__ = (
        Comment('Stashes Input/Output Operation Types'),
        Index('stashes_io_types_i_type', 'type'),
        Index('stashes_io_types_i_oper_visible', 'oper_visible'),
        Index('stashes_io_types_i_user_visible', 'user_visible'),
        Index('stashes_io_types_i_oper_cap', 'oper_cap'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'menu_name'    : _('Operation Types'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 80,
                'default_sort' : ({ 'property': 'name', 'direction': 'ASC' },),
                'grid_view' : ('name', 'class', 'type'),
                'form_view' : ('name', 'class', 'type', 'oper_visible', 'user_visible', 'operation_capability'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new operation type'))
                }
            }
        )
    id = Column(
        'siotypeid',
        UInt32(10),
        Sequence('siotypeid_seq'),
        Comment('Stash I/O ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name  = Column(
        'name',
        Unicode(255),
        Comment('Stash I/O Name'),
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    operationclass = Column(
        'class',
        OperationClass.db_type(),
        Comment('Stash I/O Class'),
        nullable=False,
        default=OperationClass.system,
        info={
            'header_string' : _('Operation Class')
            }
        )
    type_ = Column(
        'type',
        IOOperationType.db_type(),
        Comment('Stash I/O Type'),
        nullable=False,
        default=IOOperationType.inout,
        info={
            'header_string' : _('Type')
            }
        )
    oper_visible = Column(
        'oper_visible',
        NPBoolean(),
        Comment('Visibility in operator interface'),
        nullable=False,
        default=False,
        info={
            'header_string' : _('Visibility in operator interface')
            }
        )
    user_visible = Column(
        'user_visible',
        NPBoolean(),
        Comment('Visibility in user interface'),
        nullable=False,
        default=False,
        info={
            'header_string' : _('Visibility in user interface')
            }
        )
    oper_cap = Column(
        'oper_cap',
        ASCIIString(48),
        Comment('Stash I/O Required Operator Capability'),
        ForeignKey('privileges.code', name='stashes_io_types_fk_oper_cap', onupdate='CASCADE', ondelete='SET NULL'),
        info={
            'header_string' : _('Required Operator Capability')
            }
        )
    
    operation_capability = relationship('Privilege', backref=backref('stashopercap'))

    def __str__(self):
        return self.name


class StashIO(Base):
    """
    Netprofile Stashes Input/Output Operations definition
    """
    __tablename__ = 'stashes_io_def'
    __table_args__ = (
        Comment('Stashes Input/Output Operations'),
        Index('stashes_io_i_siotypeid', 'siotypeid'),
        Index('stashes_io_i_stashid', 'stashid'),
        Index('stashes_io_i_uid', 'uid'),
        Index('stashes_io_i_entityid', 'entityid'),
        Index('stashes_io_i_ts', 'ts'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'menu_name'    : _('I/O Operations'),
                'show_in_menu'  : 'modules',
                'menu_order'    : 80,
                'grid_view' : ('operation_type', 'stash', 'user', 'entity', 'ts', 'diff'),
                'form_view' : ('operation_type', 'stash', 'user', 'entity', 'ts', 'diff', 'descr'),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new operation'))
                }
            }
        )
    id = Column(
        'sioid',
        UInt32(10),
        Sequence('sioid_seq'),
        Comment('Stash I/O ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    siotypeid = Column(
        'siotypeid',
        UInt32(10),
        Comment('Stash I/O Type ID'),
        ForeignKey('stashes_io_types.siotypeid', name='stashes_io_def_fk_siotypeid', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Operation Type')
            }
        )
    stashid = Column(
        'stashid',
        UInt32(10),
        Comment('Stash ID'),
        ForeignKey('stashes_def.stashid', name='stashes_io_def_fk_stashid', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Stash')
            }
        )
    uid = Column(
        'uid',
        UInt32(10),
        Comment('User ID'),
        ForeignKey('users.uid', name='stashes_io_def_fk_uid', ondelete='SET NULL', onupdate='CASCADE'),
        info={
            'header_string' : _('User')
            }
        )
    entityid = Column(
        'entityid',
        UInt32(10),
        Comment('Related Entity ID'),
        ForeignKey('entities_def.entityid', name='stashes_io_def_fk_entityid', ondelete='SET NULL', onupdate='CASCADE'),
        info={
            'header_string' : _('Entity')
            }
        )
    ts = Column(
        'ts',
        DateTime(),
        Comment('Date of Operation'),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
        info={
            'header_string' : _('Operation Date')
            }
        )
    diff = Column(
        'diff',
        Numeric(20, 8),
        Comment('Operation Result'),
        nullable=False,
        info={
            'header_string' : _('Result')
            }
        )
    descr = Column(
        'descr',
        UnicodeText(),
        Comment('Description'),
        info={
            'header_string' : _('Description')
            }
        )
    entity = relationship('Entity',  backref=backref('operationentity', innerjoin=True))
    operation_type = relationship('StashIOType',  backref=backref('operationtype', innerjoin=True))
    stash = relationship('Stash',  backref=backref('operationstash', innerjoin=True))
    user = relationship('User', backref=backref('operationuser'))

    def __str__(self):
        return "{0}, {1}".format(self.stash, self.user)


class StashOperation(Base):
    """
    Netprofile Operations on Stashes Class Definition
    """
    __tablename__ = 'stashes_ops'
    __table_args__ = (
        Comment('Operations on Stashes'),
        Index('stashes_ops_i_stashid', 'stashid'),
        Index('stashes_ops_i_type', 'type'),
        Index('stashes_ops_i_ts', 'ts'),
        Index('stashes_ops_i_operator', 'operator'),
        Index('stashes_ops_i_entityid', 'entityid'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'menu_name'    : _('Stashes Operations'),
                'show_in_menu'  : 'modules',
                'menu_order'    : 80,
                'grid_view' : ('stash', 'type', 'ts', 'diff', 'acct_ingress', 'acct_egress'),
                'form_view' : ('stash', 'type', 'ts', 'stashoperator', 'entity', 'diff', 'acct_ingress', 'acct_egress', 'comments'),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new stash operation'))
                }
            }
        )
    id = Column(
        'stashopid',
        UInt32(20),
        Sequence('stashopid_seq'),
        Comment('Stash Operation ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
            }
        )
    stashid = Column(
        'stashid',
        UInt32(10),
        ForeignKey('stashes_def.stashid', name='stashes_ops_fk_stashid', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Stash ID'),
        nullable=False,
        info={
            'header_string': _('Stash')
            }
        )
    operation_type = Column(
        'type',
        StashOperationType.db_type(),
        Comment('Type of Operation'),
        nullable=False,
        default = StashOperationType.oper,
        info = {
            'header_string': _('Type of Operation')
            }
        )
    ts = Column(
        'ts',
        DateTime(),
        Comment('Timestamp of Operation'),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
        info={
            'header_string' : _('Timestamp')
            }
        )
    operator = Column(
        'operator',
        UInt32(10),
        ForeignKey('users.uid', name='stashes_ops_fk_operator', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Optional Operator ID'),
        info={
            'header_string' : _('Operator')
            }
        )
    entityid = Column(
        'entityid',
        UInt32(10),
        ForeignKey('entities_def.entityid', name='stashes_ops_fk_entityid', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Optional Entity ID'),
        info={
            'header_string' : _('Entity')
            }
        )
    diff = Column(
        'diff',
        Numeric(20, 8),
        Comment('Changes made to Stash'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Stash Changes')
            }
        )
    acct_ingress = Column(
        'acct_ingress',
        Numeric(16, 0),
        Comment('Accounted Ingress Traffic'),
        info={
            'header_string' : _('Ingress Traffic')
            }
        )
    acct_egress = Column(
        'acct_egress',
        Numeric(16, 0),
        Comment('Accounted Engress Traffic'),
        info={
            'header_string' : _('Engress Traffic')
            }
        )
    comments = Column(
        'comments',
        UnicodeText(),
        Comment('Optional Comments'),
        info={
            'header_string' : _('Comments')
            }
        )
    stash = relationship('Stash', backref=backref('stashoper_stash', innerjoin=True))
    stashoperator = relationship('User', backref=backref('stashoper_operator'))
    entity = relationship('Entity', backref=backref('stashoper_entity'))

    def __str__(self):
        return "{0}, {1}".format(self.stash, self.ts)
