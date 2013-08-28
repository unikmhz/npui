#!/usr/bin/env python
# -*- coding: utf-8 -*-

#thereafter python2.7 setup.py extract_messages, edit *.po, compile to *.mo, put in appropriate place et voila!
#пришлось подправить netprofile/ext/direct.py
#и netprofile_dialup/models.py
#Don't forget to reinstall dialup module 


from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

#тут возвращаем названия классов
__all__ = [
    'EnumeratedRateUsageType',
    'QuotaPeriodUnit',
    'IsPolled',
    'AdvancedFeatures',
    'IsUserSelectable',
    'BillingPeriod',
    'DestinationSets',
    'FilterSets',
    'Rates',
    'PeriodicRates',
    'RatesClasses',
    'RateClassesEtypes'
    ]

from sqlalchemy import (
    Column,
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
    validates
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
    UInt16,
    UInt32,
    UInt64,
    npbool
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

_ = TranslationStringFactory('netprofile_rates')

class EnumeratedRateUsageType(DeclEnum):
    """
    Rate Usage Type Enum class
    """
    prepaid = 'prepaid', _('Prepaid'), 10
    prepaid_cont = 'prepaid_cont', _('Prepaid Cont'), 20
    postpaid = 'postpaid', _('Postpaid'), 30
    free = 'free', _('Free'), 40

class QuotaPeriodUnit(DeclEnum):
    """
    Quota Period Unit
    """
    #what's the difference between a_day & c_day?
    a_hour = 'a_hour', _('Hour'), 10
    a_day = 'a_day', _('Day'), 20
    a_week = 'a_week', _('Week'), 30
    a_month = 'a_month', _('Month'), 40
    c_hour = 'c_hour', _('Hour'), 50
    c_day = 'c_day', _('Day'), 60
    c_month = 'c_month', _('Month'), 70

class IsPolled(DeclEnum):
    """
    Is Periodically Polled Enum class
    """
    yes   = 'Y',   _('Yes'),   10
    no   = 'N',   _('No'),   20

class AdvancedFeatures(DeclEnum):
    """
    Use Advanced Billing Features
    """
    yes   = 'Y',   _('Yes'),   10
    no   = 'N',   _('No'),   20

class IsUserSelectable(DeclEnum):
    """
    Is User Selectable?
    """
    yes   = 'Y',   _('Yes'),   10
    no   = 'N',   _('No'),   20


class BillingPeriod(Base):
    """
    Billing Periods definition
    """
    __tablename__ = 'bperiods_def'
    __table_args__ = (
        Comment('Billing Periods'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Billing Periods'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 90,
                'default_sort' : ({ 'property': 'bperiodid' ,'direction': 'ASC' },),
                'grid_view' : ('bperiodid', 'name', 'start_month', 'start_mday', 'start_wday', 'start_hour', 'start_minute',
                               'end_month', 'end_mday', 'end_wday', 'end_hour', 'end_minute'),
                'form_view' : ('bperiodid', 'name', 'start_month', 'start_mday', 'start_wday', 'start_hour', 'start_minute',
                               'end_month', 'end_mday', 'end_wday', 'end_hour', 'end_minute'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new billing period'))
                }
            }
        )
    bperiodid = Column(
        'bperiodid',
        UInt32(10),
        Comment('Billing Period ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Billing Period Name'),
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    start_month = Column(
        'start_month',
        UInt8(2),
        Comment('Start Month'),
        nullable=False,
        default=1,
        info={
            'header_string' : _('Start Month')
            }
        )
    start_mday = Column(
        'start_mday',
        UInt8(2),
        Comment('Start Day of Month'),
        nullable=False,
        default=1,
        info={
            'header_string' : _('Start Day of Month')
            }
        )
    start_wday = Column(
        'start_wday',
        UInt8(1),
        Comment('Start Day of Week'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Start Day of Week')
            }
        )
    start_hour = Column(
        'start_hour',
        UInt8(2),
        Comment('Start Hour'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Start Hour')
            }
        )
    start_minute = Column(
        'start_minute',
        UInt8(2),
        Comment('Start Minute'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Start Minute')
            }
        )
    end_month = Column(
        'end_month',
        UInt8(2),
        Comment('End Month'),
        nullable=False,
        default=12,
        info={
            'header_string' : _('End Month')
            }
        )
    end_mday = Column(
        'end_mday',
        UInt8(2),
        Comment('End Day of Month'),
        nullable=False,
        default=31,
        info={
            'header_string' : _('End Day of Month')
            }
        )
    end_wday = Column(
        'end_wday',
        UInt8(1),
        Comment('End Day of Week'),
        nullable=False,
        default=6,
        info={
            'header_string' : _('End Day of Week')
            }
        )
    end_hour = Column(
        'end_hour',
        UInt8(2),
        Comment('End Hour'),
        nullable=False,
        default=23,
        info={
            'header_string' : _('End Hour')
            }
        )
    end_minute = Column(
        'end_minute',
        UInt8(2),
        Comment('End Minute'),
        nullable=False,
        default=59,
        info={
            'header_string' : _('End Minute')
            }
        )

    billperiods = relationship('PeriodicRates', backref=backref('billingperiods', innerjoin=True))


class DestinationSets(Base):
    """
    Netprofile Accounting Destination Sets definition
    """
    __tablename__ = 'dest_sets'
    __table_args__ = (
        Comment('Accounting Destination Sets'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Accounting Destination Sets'),
                'show_in_menu'  : 'admin', #modules
                'menu_order'    : 90,
                'default_sort' : ({ 'property': 'dsid' ,'direction': 'ASC' },),
                'grid_view' : ('dsid', 'name'),
                'form_view' : ('dsid', 'name'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new accounting destination set'))
                }
            }
        )
    
    dsid = Column(
        'dsid',
        UInt32(10),
        Comment('Destination Set ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Destination Set Name'),
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    
    destsets = relationship('Rates', backref=backref("destinationsets", innerjoin=True))


class FilterSets(Base):
    """
    Netprofile Accounting Filter set definition
    """
    __tablename__ = 'filters_sets'
    __table_args__ = (
    Comment('Accounting Filter Sets'),
    {
        'mysql_engine'  : 'InnoDB',
        'mysql_charset' : 'utf8',
        'info'          : {
            #'cap_menu'      : 'BASE_NAS',
            #'cap_read'      : 'NAS_LIST',
            #'cap_create'    : 'NAS_CREATE',
            #'cap_edit'      : 'NAS_EDIT',
            #'cap_delete'    : 'NAS_DELETE',
            'menu_name'    : _('Accounting Filter Sets'),
            'show_in_menu'  : 'admin', #modules
            'menu_order'    : 90,
            'default_sort' : ({ 'property': 'fsid' ,'direction': 'ASC' },),
            'grid_view' : ('fsid', 'name'),
            'form_view' : ('fsid', 'name'),
            'easy_search' : ('name',),
            'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
            'create_wizard' : SimpleWizard(title=_('Add new accounting filter set'))
            }
        }
    )
    
    fsid = Column(
        'fsid',
        UInt32(10),
        Comment('Filter Set ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Filter Set Name'),
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    fsets = relationship('Rates', backref=backref("filtersets", innerjoin=True))


class Rates(Base):
    """
    Netprofile Payment Rates definition
    """
    __tablename__ = 'rates_def'
    __table_args__ = (
        Comment('Network Access Servers'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Payment Rates'),
                'show_in_menu'  : 'modules',
                'menu_main'     : True,
                'menu_order'    : 90,
                'default_sort' : ({ 'property': 'rateid' ,'direction': 'ASC' },),
                'grid_view' : ('rateid', 'name', 'type', 'qp_amount', 'qp_unit', 'qsum'),
                'form_view' : ('rateid', 'type', 'name', 'polled', 'abf', 'usersel', 'rateclasses', 'ippoolselements', 'destinationsets', 'filtersets', 'qp_amount', 'qp_unit', 'qsum', 'auxsum', 'qt_ingress', 'qt_egress', 'qsec', 'oqsum_ingress', 'oqsum_egress', 'oqsum_sec', 'sim', 'block_timeframe', 'cb_qsum_before', 'cb_qsum_success', 'cb_qsum_failure', 'cb_after_connect', 'cb_after_disconnect', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new payment rate'))
                }
            }
        )
    
    rateid = Column(
        'rateid',
        UInt32(10),
        Comment('ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    type_ = Column(
        'type',
        EnumeratedRateUsageType.db_type(),
        Comment('Rate Usage Type'),
        nullable=False,
        default=EnumeratedRateUsageType.prepaid,
        info={
            'header_string' : _('Rate Type')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Rate Name'),
        nullable=False,
        info={
            'header_string' : _('Rate Name')
            }
        )
    polled = Column(
        'polled',
        IsPolled.db_type(),
        Comment('Is Periodically Polled?'),
        nullable=False,
        default=IsPolled.no,
        info={
            'header_string' : _('Is Periodically Polled?')
            }
        )
    abf = Column(
        'abf',
        AdvancedFeatures.db_type(),
        Comment('Use Advanced Billing Features'),
        nullable=False,
        default=AdvancedFeatures.no,
        info={
            'header_string' : _('Advanced Billing Features')
            }
        )
    usersel = Column(
        'usersel',
        IsUserSelectable.db_type(),
        Comment('Is User Selectable?'),
        nullable=False,
        default=IsUserSelectable.no,
        info={
            'header_string' : _('Is User Selectable?')
            }
        )
    rcid = Column(
        'rcid',
        UInt32(10),
        Comment('Rate Class ID'),
        ForeignKey('rates_classes_def.rcid', name='rates_def_fk_rcid', onupdate='CASCADE'),
        info={
            'header_string' : _('Rate Class')
            }
        )
    poolid = Column(
        'poolid',
        UInt32(10),
        ForeignKey('ippool_def.poolid', name='rates_def_fk_poolid', onupdate='CASCADE'),
        Comment('IP Address Pool ID'),
        info={
            'header_string' : _('IP Address Pool')
            }
        )
    dsid = Column(
        'dsid', 
        UInt32(10),
        ForeignKey('dest_sets.dsid', name='rates_def_ibfk_1', onupdate='CASCADE'),
        )
    fsid = Column(
        'fsid',
        UInt32(10),
        ForeignKey('filters_sets.fsid', name='rates_def_ibfk_2', onupdate='CASCADE'),
        )
    qp_amount = Column(
        'qp_amount',
        UInt32(5),
        Comment('Quota Period Amount'),
        nullable=False,
        default=1,
        info={
            'header_string' : _('Quota Period Amount')
            }
        )
    qp_unit = Column(
        'qp_unit',
        QuotaPeriodUnit.db_type(),
        Comment('Quota Period Unit'),
        nullable=False,
        default=QuotaPeriodUnit.c_month,
        info={
            'header_string' : _('Quota Period Unit')
            }
        )
    qsum = Column(
        'qsum',
        Numeric(20, 8),
        Comment('Quota Sum'),
        nullable=False,
        default=0.0,
        info={
            'header_string' : _('Quota Sum')
            }
        )

    auxsum = Column(
        'auxsum',
        Numeric(20, 8),
        Comment('Auxillary Sum'),
        nullable=False,
        default=0.0,
        info={
            'header_string' : _('Auxillary Sum')
            }
        )
    qt_ingress = Column(
        'qt_ingress',
        Numeric(16, 0),
        Comment('Quota Ingress Traffic in Bytes'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Quota Ingress Traffic')
            }
        )
    qt_egress= Column(
        'qt_egress',
        Numeric(16, 0),
        Comment('Quota Egress Traffic in Bytes'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Quota Egress Traffic')
            }
        )
    #???
    qsec = Column(
        'qsec',
        UInt32(10),
        nullable=False,
        default=0
        )
    oqsum_ingress = Column(
        'oqsum_ingress',
        Numeric(20, 8),
        Comment('Over Quota Ingress Payment per Byte'),
        nullable=False,
        default=0.0,
        info={
            'header_string' : _('Over Quota Ingress Payment')
            }
        )
    oqsum_egress = Column(
        'oqsum_egress',
        Numeric(20, 8),
        Comment('Over Quota Egress Payment per Byte'),
        nullable=False,
        default=0.0,
        info={
            'header_string' : _('Over Quota Egress Payment')
            }
        )
    oqsum_sec = Column(
        'oqsum_sec',
        Numeric(20, 8),
        nullable=False,
        default=0.0,
        )
    sim = Column(
        'sim',
        UInt32(6),
        Comment('Number of Simultaneous Uses'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Number of Simultaneous Uses')
            }
        )
    pol_ingress = Column(
        'pol_ingress',
        Unicode(255),
        Comment('Ingress Traffic Policy'),
        info={
            'header_string' : _('Ingress Traffic Policy')
            }
        )
    pol_egress = Column(
        'pol_egress',
        Unicode(255),
        Comment('Egress Traffic Policy'),
        info={
            'header_string' : _('Egress Traffic Policy')
            }
        )
    block_timeframe = Column(
        'block_timeframe',
        UInt8(5),
        Comment('Max Continuous Blocking Time (in accounting periods)'),
        info={
            'header_string' : _('Max Continuous Blocking Time')
            }
        )

    cb_qsum_before = Column(
        'cb_qsum_before',
        Unicode(255),
        Comment('Callback before Quota Payment'),
        info={
            'header_string' : _('Callback before Quota Payment')
            }
        )
    cb_qsum_success = Column(
        'cb_qsum_success',
        Unicode(255),
        Comment('Callback on Successful Quota Payment'),
        info={
            'header_string' : _('Callback on Successful Quota Payment')
            }
        )
    cb_qsum_failure = Column(
        'cb_qsum_failure',
        Unicode(255),
        Comment('Callback on Failed Quota Payment'),
        info={
            'header_string' : _('Callback on Failed Quota Payment')
            }
        )
    cb_after_connect = Column(
        'cb_after_connect',
        Unicode(255),
        Comment('Callback after Connecting'),
        info={
            'header_string' : _('Callback after Connecting')
            }
        )
    cb_after_disconnect= Column(
        'cb_after_disconnect',
        Unicode(255),
        Comment('Callback after Disconnecting'),
        info={
            'header_string' : _('Callback after Disconnecting')
            }
        )
    descr = Column(
        'descr',
        Unicode(255),
        Comment('Rate Description'),
        info={
            'header_string' : _('Description')
            }
        )

    def __str__(self):
        return "{0}".format(self.name)

class PeriodicRates(Base):
    """
    Periodic Rate Modifiers
    """
    __tablename__ = 'rates_periodic'
    __table_args__ = (        
        Comment('Periodic Rate Modifiers'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Periodic Rate Modifiers'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 70,
                'default_sort' : ({ 'property': 'rpid' ,'direction': 'ASC' },),
                'grid_view' : ('rpid', 'billingperiods', 'oqsum_ingress_mul', 'oqsum_egress_mul'),
                'form_view' : ('rpid', 'billingperiods', 'oqsum_ingress_mul', 'oqsum_egress_mul'),
                'easy_search' : ('idstr',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new Periodic Rate Modifier'))
                }
            }
        )
    rpid = Column(
        'rpid',
        UInt32(10),
        Comment('Periodic Rate Modifier ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    bperiodid = Column(
        'bperiodid',
        UInt32(10),
        ForeignKey('bperiods_def.bperiodid', name='rates_periodic_fk_bperiodid', onupdate='CASCADE'),
        Comment('Billing Period ID'),
        nullable=False,
        info={
            'header_string' : _('Billing Period')
            }
        )
    oqsum_ingress_mul = Column(
        'oqsum_ingress_mul',
        Numeric(16, 8),
        Comment('Ingress Overquota Sum Multiplier'),
        nullable=False,
        default=1.0,
        info={
            'header_string' : _('Ingress Overquota Sum Multiplier')
            }
        )
    oqsum_egress_mul = Column(
        'oqsum_egress_mul',
        Numeric(16, 8),
        Comment('Egress Overquota Sum Multiplier'),
        nullable=False,
        default=1.0,
        info={
            'header_string' : _('Egress Overquota Sum Multiplier')
            }
        )

class RatesClasses(Base):
    """
    Rate Classes
    """
    __tablename__ = 'rates_classes_def'
    __table_args__ = (
        Comment('Rate Classes'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Rate Classes'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 80,
                'default_sort' : ({ 'property': 'rcid' ,'direction': 'ASC' },),
                'grid_view' : ('rcid', 'name', 'descr',),
                'form_view' : ('rcid', 'name', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new rate class'))
                }
            }
        )
    rcid = Column(
        'rcid',
        UInt32(10),
        Comment('Rate Class ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Rate Class Name'),
        nullable=False,
        info={
            'header_string' : _('Rate Class Name')
            }
        )
    descr = Column(
        'descr',
        UnicodeText(),
        Comment('Rate Class Description'),
        info={
            'header_string' : _('Description')
            }
        )
    rateclasses_elements = relationship("Rates", backref=backref('rateclasses', innerjoin=True))
    rateclasseselements = relationship("RateClassesEtypes", backref=backref('rateclasses', innerjoin=True))

    def __str__(self):
        return "%s" % str(self.name)
    

class RateClassesEtypes(Base):
    """
    Rate Class Mappings to Entity Types
    """
    __tablename__ = 'rates_classes_etypes'
    __table_args__ = (
        Comment('Rate Class Mappings to Entity Types'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Rate Classes Mappings to Entity Types'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 80,
                'default_sort' : ({ 'property': 'rcmapid' ,'direction': 'ASC' },),
                'grid_view' : ('rcmapid', 'rateclasses', 'etype'),
                'form_view' : ('rcmapid', 'rateclasses', 'etype'),
                'easy_search' : ('etype',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new rate class mapping to entity type'))
                }
            }
        )
    rcmapid = Column(
        'rcmapid',
        UInt32(10),
        Comment('Rate Class Mapping ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    rcid = Column(
        'rcid',
        UInt32(10),
        ForeignKey('rates_classes_def.rcid', name='rates_classes_etypes_fk_rcid', onupdate='CASCADE'),
        Comment('Rate Class ID'),
        nullable=False,
        info={
            'header_string' : _('Rate ID')
            }
        )
    etype = Column(
        'etype',
        Unicode(32),
        Comment('Entity Type'),
        nullable=False,
        info={
            'header_string' : _('Entity Type')
            }
        )

