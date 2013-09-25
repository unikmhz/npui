#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division
    )

__all__ = [
    'Host',
    'HostAlias',
    'HostReal',
    'HostGroup'
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
    Text,
    TIMESTAMP, 
    FetchedValue,
    func
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


class Host(Base):
    """
    Netprofile Host definition
    """
    __tablename__ = 'hosts_def'
    __table_args__ = (
        Comment('Hosts'),
        Index('hosts_def_u_hostname', 'domainid', 'name', unique=True),
        Index('hosts_def_i_hgid', 'hgid'),
        Index('hosts_def_i_entityid', 'entityid'),
        Index('hosts_def_i_aliasid', 'aliasid'),
        Index('hosts_def_i_cby', 'cby'),
        Index('hosts_def_i_mby', 'mby'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'menu_name'    : _('Hosts'),
                'show_in_menu'  : 'modules',
                'menu_order'    : 80,
                'menu_main'     : True,
                'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
                'grid_view' : ('group', 'entity', 'domain', 'name', 'alias', 'ctime', 'mtime', 'createuser', 'modifyuser', 'descr'),
                'form_view' : ('group', 'entity', 'domain', 'name', 'alias', 'ctime', 'mtime', 'createuser', 'modifyuser', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new host'))
                }
            }
        )
    id = Column(
        'hostid',
        UInt32(),
        Sequence('hostid_seq'),
        Comment('Host ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    hgid = Column(
        'hgid',
        UInt32(),
        ForeignKey('hosts_groups.hgid', name='hosts_def_fk_hgid', onupdate='CASCADE'),
        Comment('Host Group ID'),
        nullable=False,
        info={
            'header_string' : _('Group')
            }
        )
    entityid = Column(
        'entityid',
        UInt32(),
        ForeignKey('entities_def.entityid', name='hosts_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Entity ID'),
        nullable=False,
        info={
            'header_string' : _('Entity')
            }
        )
    domainid = Column(
        'domainid',
        UInt32(),
        ForeignKey('domains_def.domainid', name='hosts_def_fk_domainid', onupdate="CASCADE"),
        Comment('Domain ID'),
        nullable=False,
        info={
            'header_string' : _('Domain')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Host Name'),
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    aliasid = Column(
        'aliasid',
        UInt32(),
        ForeignKey('hosts_def.hostid', name='hosts_def_fk_aliasid', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Alias')
            }
        )
    ctime = Column(
        'ctime',
        TIMESTAMP(),
        Comment('Time of Creation'),
        nullable=True,
        default=None,
        server_default=FetchedValue(),
        info={
            'header_string' : _('Created'),
            'read_only'     : True
            }
        )
    mtime = Column(
        'mtime',
        TIMESTAMP(),
        Comment('Time of Last Modification'),
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        info={
            'header_string' : _('Modified'),
            'read_only'     : True
            }
        )
    cby = Column(
        'cby',
        UInt32(),
        ForeignKey('users.uid', name='hosts_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Created By'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Created by'),
            'read_only'     : True
            }
        )
    mby = Column(
        'mby',
        UInt32(),
        ForeignKey('users.uid', name='hosts_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Last Modified By'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Modified by'),
            'read_only'     : True
            }
        )
    descr = Column(
        'descr',
        UnicodeText(),
        Comment('Host description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Description')
            }
        )

    group = relationship('HostGroup', backref=backref('hostgroup', innerjoin=True))
    entity = relationship('Entity', backref=backref('hostentities', innerjoin=True))
    domain = relationship('Domain', backref=backref('hostdomains', innerjoin=True))
    alias = relationship('Host', backref=backref('hostaliases'), remote_side=id)
    createuser = relationship('User', backref=backref('hostcreateuser'), foreign_keys=cby)
    modifyuser = relationship('User', backref=backref('hostmodifyuser'), foreign_keys=mby)
    
    def __str__(self):
        return '%s' % str(self.name)


class HostGroup(Base):
    """
    Netprofile Host Group Description
    """
    __tablename__ = 'hosts_groups'
    __table_args__ = (
        Comment('Hosts Groups'),
        Index('hosts_groups_u_hgname', 'name', unique=True),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_HOST',
                #'cap_read'      : 'HOST_LIST',
                #'cap_create'    : 'HOST_CREATE',
                #'cap_edit'      : 'HOST_EDIT',
                #'cap_delete'    : 'HOST_DELETE',
                'menu_name'    : _('Hosts Groups'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 80,
                'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
                'grid_view' : ('name', 'public', 'startoffset', 'endoffset', 'startoffset6', 'endoffset6', 'use_hwaddr', 'use_dhcp', 'use_banning'
                               #'name', 
                               #MarkupColumn(
                               #name='state',
                               #header_string=_('State'),
                               #template=TemplateObject('netprofile_hosts:templates/hosts_icons.mak'),
                               #column_width=60,
                               #column_resizable=False
                               #)
                               ),
                'form_view' : ('name', 'public', 'startoffset', 'endoffset', 'startoffset6', 'endoffset6', 'use_hwaddr', 'use_dhcp', 'use_banning'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new host group'))
                }
            }
        )
    id = Column(
        'hgid',
        UInt32(),
        Sequence('hgid_seq'),
        Comment('Host Group ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Host Group Name'),
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    public = Column(
        'public',
        NPBoolean(),
        Comment('Is host group globally visible?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string' : _('Is Public?')
            }
        )
    startoffset = Column(
        'startoffset',
        UInt8(5),
        Comment('IP Allocator Start Offset'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('Start Offset')
            }
        )
    endoffset = Column(
        'endoffset',
        UInt8(5),
        Comment('IP Allocator End Offset'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('End Offset')
            }
        )
    startoffset6 = Column(
        'startoffset6',
        UInt32(20),
        Comment('IPv6 Allocator Start Offset'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('IPv6 Start Offset')
            }
        )
    endoffset6 = Column(
        'endoffset6',
        UInt32(20),
        Comment('IPv6 Allocator End Offset'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('IPv6 End Offset')
            }
        )
    use_hwaddr = Column(
        'use_hwaddr',
        NPBoolean(),
        Comment('Use Unique Hardware Check'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string' : _('Unique Hardware Check')
            }
        )
    use_dhcp = Column(
        'use_dhcp',
        NPBoolean(),
        Comment('Use DHCP'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string' : _('DHCP')
            }
        )
    use_banning = Column(
        'use_banning',
        NPBoolean(),
        Comment('Use Banning System'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string' : _('Banning System')
            }
        )
    

    def __str__(self):
        return "%s" % self.name


class HostAlias(Base):
    """
    Netprofile Host Alias definition
    """
    __tablename__ = 'hosts_aliases'
    __table_args__ = (
        Comment('Hosts Aliases'),
        Index('hosts_def_u_hostname', 'domainid', 'name', unique=True),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
        #'cap_menu'      : 'BASE_HOST',
                #'cap_read'      : 'HOST_LIST',
                #'cap_create'    : 'HOST_CREATE',
                #'cap_edit'      : 'HOST_EDIT',
                #'cap_delete'    : 'HOST_DELETE',
                'menu_name'    : _('Hosts Aliases'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 80,
                'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
                'grid_view' : ('name', 'group', 'entity', 'domain', 'alias', 'ctime', 'mtime', 'createuser', 'modifyuser', 'descr'),
                'form_view' : ('name', 'group', 'entity', 'domain', 'alias', 'ctime', 'mtime', 'createuser', 'modifyuser', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new host alias'))
                }
            }
        )
    
    id = Column(
        'hostid',
        UInt32(),
        Sequence('hostid_seq'),
        Comment('Host ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    hgid = Column(
        'hgid',
        UInt32(),
        ForeignKey('hosts_groups.hgid', name='hosts_def_fk_hgid', onupdate='CASCADE'),
        Comment('Host Group ID'),
        nullable=False,
        info={
            'header_string' : _('Group')
            }
        )
    entityid = Column(
        'entityid',
        UInt32(),
        ForeignKey('entities_def.entityid', name='hosts_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Entity ID'),
        nullable=False,
        info={
            'header_string' : _('Entity')
            }
        )
    domainid = Column(
        'domainid',
        UInt32(),
        ForeignKey('domains_def.domainid', name='hosts_def_fk_domainid', onupdate="CASCADE"),
        Comment('Domain ID'),
        nullable=False,
        info={
            'header_string' : _('Domain')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Host Name'),
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    aliasid = Column(
        'aliasid',
        UInt32(),
        ForeignKey('hosts_def.hostid', name='hosts_def_fk_aliasid', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Alias')
            }
        )
    ctime = Column(
        'ctime',
        TIMESTAMP(),
        Comment('Time of Creation'),
        nullable=True,
        default=None,
        server_default=FetchedValue(),
        info={
            'header_string' : _('Created'),
            'read_only'     : True
            }
        )
    mtime = Column(
        'mtime',
        TIMESTAMP(),
        Comment('Time of Last Modification'),
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        info={
            'header_string' : _('Modified'),
            'read_only'     : True
            }
        )
    cby = Column(
        'cby',
        UInt32(),
        ForeignKey('users.uid', name='hosts_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Created By'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Created by'),
            'read_only'     : True
            }
        )
    mby = Column(
        'mby',
        UInt32(),
        ForeignKey('users.uid', name='hosts_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Last Modified By'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Modified by'),
            'read_only'     : True
            }
        )

    descr = Column(
        'descr',
        UnicodeText(),
        Comment('Host description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Description')
            }
        )

    entity = relationship('Entity', backref=backref('hostaliasentities', innerjoin=True))
    domain = relationship('Domain', backref=backref('hostaliasdomains', innerjoin=True))    
    createuser = relationship('User', backref=backref('hostaliascreateuser'), foreign_keys=cby)
    modifyuser = relationship('User', backref=backref('hostaliasmodifyuser'), foreign_keys=mby)
    alias = relationship('Host', backref=backref('hostaliasaliases'))
    group = relationship('HostGroup', backref=backref('hostaliasgroup', innerjoin=True))

    def __str__(self):
        return '%s' % str(self.name)


class HostReal(Base):
    """
    Netprofile Host Real definition
    """
    __tablename__ = 'hosts_real'
    __table_args__ = (
        Comment('Hosts Real'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_HOST',
                #'cap_read'      : 'HOST_LIST',
                #'cap_create'    : 'HOST_CREATE',
                #'cap_edit'      : 'HOST_EDIT',
                #'cap_delete'    : 'HOST_DELETE',
                'menu_name'    : _('Hosts Real'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 80,
                'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
                'grid_view' : ('name', 'group', 'entity', 'domain', 'ctime', 'mtime', 'createuser', 'modifyuser', 'descr'),
                'form_view' : ('name', 'group', 'entity', 'domain', 'ctime', 'mtime', 'createuser', 'modifyuser', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new real host'))
                }
            }
        )
    
    id = Column(
        'hostid',
        UInt32(),
        Sequence('hostid_seq'),
        Comment('Host ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    hgid = Column(
        'hgid',
        UInt32(),
        ForeignKey('hosts_groups.hgid', name='hosts_def_fk_hgid', onupdate='CASCADE'),
        Comment('Host Group ID'),
        nullable=False,
        info={
            'header_string' : _('Group')
            }
        )
    entityid = Column(
        'entityid',
        UInt32(),
        ForeignKey('entities_def.entityid', name='hosts_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Entity ID'),
        nullable=False,
        info={
            'header_string' : _('Entity')
            }
        )
    domainid = Column(
        'domainid',
        UInt32(),
        ForeignKey('domains_def.domainid', name='hosts_def_fk_domainid', onupdate="CASCADE"),
        Comment('Domain ID'),
        nullable=False,
        info={
            'header_string' : _('Domain')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Host Name'),
        nullable=False,
        info={
            'header_string' : _('Host Name')
            }
        )
    ctime = Column(
        'ctime',
        TIMESTAMP(),
        Comment('Time of Creation'),
        nullable=True,
        default=None,
        server_default=FetchedValue(),
        info={
            'header_string' : _('Created'),
            'read_only'     : True
            }
        )
    mtime = Column(
        'mtime',
        TIMESTAMP(),
        Comment('Time of Last Modification'),
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        info={
            'header_string' : _('Modified'),
            'read_only'     : True
            }
        )
    cby = Column(
        'cby',
        UInt32(),
        ForeignKey('users.uid', name='hosts_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Created By'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Created by'),
            'read_only'     : True
            }
        )
    mby = Column(
        'mby',
        UInt32(),
        ForeignKey('users.uid', name='hosts_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Last Modified By'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Modified by'),
            'read_only'     : True
            }
        )
    descr = Column(
        'descr',
        UnicodeText(),
        Comment('Host description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Description')
            }
        )

    entity = relationship('Domain', backref=backref('hostrealentities', innerjoin=True))
    domain = relationship('Domain', backref=backref('hostrealdomains', innerjoin=True))    
    createuser = relationship('User', backref=backref('hostrealcreateuser'), foreign_keys=cby)
    modifyuser = relationship('User', backref=backref('hostrealmodifyuser'), foreign_keys=mby)
    group = relationship('HostGroup', backref=backref('hostrealgroup', innerjoin=True))
    
    def __str__(self):
        return '%s' % str(self.name)
