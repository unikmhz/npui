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

from netprofile_entities.models import Entity
from netprofile_domains.models import Domain
from netprofile_core.models import User

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
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
		#'cap_menu'      : 'BASE_HOST',
                #'cap_read'      : 'HOST_LIST',
                #'cap_create'    : 'HOST_CREATE',
                #'cap_edit'      : 'HOST_EDIT',
                #'cap_delete'    : 'HOST_DELETE',
                'menu_name'    : _('Hosts'),
                'show_in_menu'  : 'modules',
                'menu_order'    : 80,
                'menu_main'     : True,
                'default_sort' : ({ 'property': 'hostid' ,'direction': 'ASC' },),
                'grid_view' : ('hostgroup', 'hostentities', 'hostdomains', 'name', 'ctime', 'mtime', 'hostcreateuser', 'hostmodifyuser', 'descr'),
                'form_view' : ('hostgroup', 'hostentities', 'hostdomains', 'name', 'ctime', 'mtime', 'hostcreateuser', 'hostmodifyuser', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new host'))
                }
            }
        )
	
    hostid = Column(
	    'hostid',
	    UInt32(10),
	    Comment('Host ID'),
	    primary_key=True,
	    nullable=False,
	    info={
		    'header_string' : _('ID')
		    }
	    )
    hgid = Column(
	    'hgid',
	    UInt32(10),
            #hostgroup
            ForeignKey('hosts_groups.hgid', name='hosts_def_fk_hgid', onupdate='CASCADE'),
	    Comment('Host Group ID'),
	    nullable=False,
	    info={
		    'header_string' : _('Host Group')
		    }
	    )
    entityid = Column(
	    'entityid',
	    UInt32(10),
            #hostentities
            ForeignKey('entities_def.entityid', name='hosts_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
	    Comment('Entity ID'),
	    nullable=False,
	    info={
		    'header_string' : _('Entity')
		    }
	    )
    domainid = Column(
	    'domainid',
	    UInt32(10),
            #hostdomains
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
	    UInt32(10),
            #hostaliases
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
	    UInt32(10),
            #hostcreateuser
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
	    UInt32(10),
            #hostmodifyuser
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
    
    Entity.hostentities = relationship('Host', backref=backref('hostentities', innerjoin=True))
    Domain.hostdomains = relationship('Host', backref=backref('hostdomains', innerjoin=True))
    hostsaliases = relationship('Host', backref=backref('hostaliases', innerjoin=True), remote_side=hostid)
    User.hostcreateuser = relationship('Host', backref=backref('hostcreateuser', innerjoin=True), foreign_keys=cby)
    User.hostmodifyuser = relationship('Host', backref=backref('hostmodifyuser', innerjoin=True), foreign_keys=mby)
    hostaliasaliases = relationship('HostAlias', backref=backref('hostaliasaliases', innerjoin=True), remote_side=hostid)
    def __str__(self):
	    return '%s' % str(self.name)


class HostGroup(Base):
    """
    Netprofile Host Group Description
    """
    __tablename__ = 'hosts_groups'
    __table_args__ = (
        Comment('Hosts Groups'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
		#'cap_menu'      : 'BASE_HOST',
                #'cap_read'      : 'HOST_LIST',
                #'cap_create'    : 'HOST_CREATE',
                #'cap_edit'      : 'HOST_EDIT',
                #'cap_delete'    : 'HOST_DELETE',
                'menu_name'    : _('Hosts groups'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 80,
                'default_sort' : ({ 'property': 'hgid' ,'direction': 'ASC' },),
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
    hgid = Column(
        'hgid',
        UInt32(10),
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
            'header_string' : _('Host Group Name')
            }
        )
    public = Column(
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
        NPBoolean(),
        Comment('Use Unique Hardware Check'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string' : _('Use Unique Hardware Check')
            }
        )
    use_dhcp = Column(
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
        NPBoolean(),
        Comment('Use Banning System'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string' : _('Use Banning System')
            }
        )

    hostgroup = relationship('Host', backref=backref('hostgroup', innerjoin=True))
    hostaliasgroup = relationship('HostAlias', backref=backref('hostaliasgroup', innerjoin=True))
    hostrealgroup = relationship('HostReal', backref=backref('hostrealgroup', innerjoin=True))

    def __str__(self):
        return "%s" % self.name


class HostAlias(Base):
    """
    Netprofile Host Alias definition
    """
    __tablename__ = 'hosts_aliases'
    __table_args__ = (
        Comment('Hosts Aliases'),
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
                'default_sort' : ({ 'property': 'hostid' ,'direction': 'ASC' },),
                'grid_view' : ('name', 'hostaliasgroup', 'hostaliasentities', 'hostaliasdomains', 'hostaliasaliases', 'ctime', 'mtime', 'hostaliascreateuser', 'hostaliasmodifyuser', 'descr'),
                'form_view' : ('hostid', 'name'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new host alias'))
                }
            }
        )
	
    hostid = Column(
	    'hostid',
	    UInt32(10),
	    Comment('Host ID'),
	    primary_key=True,
	    nullable=False,
	    info={
		    'header_string' : _('ID')
		    }
	    )
    hgid = Column(
	    'hgid',
	    UInt32(10),
            #hostaliasgroup
            ForeignKey('hosts_groups.hgid', name='hosts_def_fk_hgid', onupdate='CASCADE'),
	    Comment('Host Group ID'),
	    nullable=False,
	    info={
		    'header_string' : _('Host Group')
		    }
	    )
    entityid = Column(
	    'entityid',
	    UInt32(10),
            #hostaliasentities
            ForeignKey('entities_def.entityid', name='hosts_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
	    Comment('Entity ID'),
	    nullable=False,
	    info={
		    'header_string' : _('Entity')
		    }
	    )
    domainid = Column(
	    'domainid',
	    UInt32(10),
            #hostaliasdomains
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
    aliasid = Column(
	    'aliasid',
	    UInt32(10),
            #hostaliasaliases
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
	    UInt32(10),
            #hostaliascreateuser
            ForeignKey('users.uid', name='hosts_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
	    Comment('Created By'),
	    nullable=True,
	    default=None,
	    server_default=text('NULL'),
	    info={
		    'header_string' : _('Created'),
		    'read_only'     : True
		    }
	    )
    mby = Column(
	    'mby',
	    UInt32(10),
            #hostaliasmodifyuser
            ForeignKey('users.uid', name='hosts_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
	    Comment('Last Modified By'),
	    nullable=True,
	    default=None,
	    server_default=text('NULL'),
	    info={
		    'header_string' : _('Modified'),
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
    Entity.hostaliasentities = relationship('HostAlias', backref=backref('hostaliasentities', innerjoin=True))
    Domain.hostaliasdomains = relationship('HostAlias', backref=backref('hostaliasdomains', innerjoin=True))    
    User.hostaliascreateuser = relationship('HostAlias', backref=backref('hostaliascreateuser', innerjoin=True), foreign_keys=cby)
    User.hostaliasmodifyuser = relationship('HostAlias', backref=backref('hostaliasmodifyuser', innerjoin=True), foreign_keys=mby)

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
                'default_sort' : ({ 'property': 'hostid' ,'direction': 'ASC' },),
                'grid_view' : ('name', 'hostrealgroup', 'hostrealentities', 'hostrealdomains', 'ctime', 'mtime', 'hostrealcreateuser', 'hostrealmodifyuser', 'descr'),
                'form_view' : ('name', 'hostrealgroup', 'hostrealentities', 'hostrealdomains', 'ctime', 'mtime', 'hostrealcreateuser', 'hostrealmodifyuser', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new real host'))
                }
            }
        )
	
    hostid = Column(
	    'hostid',
	    UInt32(10),
	    Comment('Host ID'),
	    primary_key=True,
	    nullable=False,
	    info={
		    'header_string' : _('ID')
		    }
	    )
    hgid = Column(
	    'hgid',
	    UInt32(10),
            #hostrealgroup
            ForeignKey('hosts_groups.hgid', name='hosts_def_fk_hgid', onupdate='CASCADE'),
	    Comment('Host Group ID'),
	    nullable=False,
	    info={
		    'header_string' : _('Host Group')
		    }
	    )
    entityid = Column(
	    'entityid',
	    UInt32(10),
            #hostrealentities
            ForeignKey('entities_def.entityid', name='hosts_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
	    Comment('Entity ID'),
	    nullable=False,
	    info={
		    'header_string' : _('Entity')
		    }
	    )
    domainid = Column(
	    'domainid',
	    UInt32(10),
            #hostrealdomains
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
	    UInt32(10),
            #hostrealcreateuser
            ForeignKey('users.uid', name='hosts_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
	    Comment('Created By'),
	    nullable=True,
	    default=None,
	    server_default=text('NULL'),
	    info={
		    'header_string' : _('Created'),
		    'read_only'     : True
		    }
	    )
    mby = Column(
	    'mby',
	    UInt32(10),
            #hostrealmodifyuser
            ForeignKey('users.uid', name='hosts_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
	    Comment('Last Modified By'),
	    nullable=True,
	    default=None,
	    server_default=text('NULL'),
	    info={
		    'header_string' : _('Modified'),
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

    Entity.hostrealentities = relationship('HostReal', backref=backref('hostrealentities', innerjoin=True))
    Domain.hostrealdomains = relationship('HostReal', backref=backref('hostrealdomains', innerjoin=True))    
    User.hostrealcreateuser = relationship('HostReal', backref=backref('hostrealcreateuser', innerjoin=True), foreign_keys=cby)
    User.hostrealmodifyuser = relationship('HostReal', backref=backref('hostrealmodifyuser', innerjoin=True), foreign_keys=mby)

    
    def __str__(self):
	    return '%s' % str(self.name)
