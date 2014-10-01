#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Hosts module
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
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

from netprofile.common.modules import ModuleBase

from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_hosts')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_hosts:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('entities', 'domains')

	@classmethod
	def get_models(cls):
		from netprofile_hosts import models
		return (
			models.DomainService,
			models.Host,
			models.HostGroup,
			models.Service,
			models.ServiceType
		)

	@classmethod
	def get_sql_functions(cls):
		from netprofile_hosts import models
		return (
			models.HostCreateAliasProcedure,
		)

	@classmethod
	def get_sql_views(cls):
		from netprofile_hosts import models
		return (
			models.HostsAliasesView,
			models.HostsRealView
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_hosts.models import (
			ServiceType,
			ServiceProtocol
		)
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		sess.add(LogType(
			id=4,
			name='Hosts'
		))
		sess.add(LogType(
			id=10,
			name='Services'
		))
		sess.flush()

		privs = (
			Privilege(
				code='BASE_HOSTS',
				name='Access: Hosts'
			),
			Privilege(
				code='HOSTS_LIST',
				name='Host: List'
			),
			Privilege(
				code='HOSTS_CREATE',
				name='Hosts: Create'
			),
			Privilege(
				code='HOSTS_EDIT',
				name='Hosts: Edit'
			),
			Privilege(
				code='HOSTS_DELETE',
				name='Hosts: Delete'
			),
			Privilege(
				code='HOSTS_GROUPS_CREATE',
				name='Hosts: Create groups'
			),
			Privilege(
				code='HOSTS_GROUPS_EDIT',
				name='Hosts: Edit groups'
			),
			Privilege(
				code='HOSTS_GROUPS_DELETE',
				name='Hosts: Delete groups'
			),
			Privilege(
				code='BASE_SERVICES',
				name='Access: Services'
			),
			Privilege(
				code='SERVICES_LIST',
				name='Services: List'
			),
			Privilege(
				code='SERVICES_CREATE',
				name='Services: Create'
			),
			Privilege(
				code='SERVICES_EDIT',
				name='Services: Edit'
			),
			Privilege(
				code='SERVICES_DELETE',
				name='Services: Delete'
			),
			Privilege(
				code='SERVICES_TYPES_CREATE',
				name='Services: Create types'
			),
			Privilege(
				code='SERVICES_TYPES_EDIT',
				name='Services: Edit types'
			),
			Privilege(
				code='SERVICES_TYPES_DELETE',
				name='Services: Delete types'
			)
		)
		for priv in privs:
			priv.module = modobj
			sess.add(priv)
		try:
			grp_admins = sess.query(Group).filter(Group.name == 'Administrators').one()
			for priv in privs:
				cap = GroupCapability()
				cap.group = grp_admins
				cap.privilege = priv
		except NoResultFound:
			pass

		stypes = (
			('domain', 'Domain Name System', 'tcp', 53, 53, 'dns,nameserver'),
			('domain', 'Domain Name System', 'udp', 53, 53, 'dns,nameserver'),
			('ftp', 'File Transfer Protocol', 'tcp', 21, 21, 'fsp, fspd, fxp'),
			('ftp-data', 'File Transfer Protocol Data Stream', 'tcp', 20, 20, 'fsp-data,fspd-data,fxp-data'),
			('imap', 'Internet Message Access Protocol', 'tcp', 143, 143, 'imap2'),
			('imaps', 'Internet Message Access Protocol over SSL', 'tcp', 993, 993, 'imap2s,simap'),
			('nntp', 'Network News Transfer Protocol', 'tcp', 119, 119, 'readnews,untp'),
			('nntps', 'Network News Transfer Protocol over SSL', 'tcp', 563, 563, 'untps,snntp'),
			('pop3', 'Post Office Protocol version 3', 'tcp', 110, 110, 'pop-3'),
			('pop3s', 'Post Office Protocol version 3 over SSL', 'tcp', 995, 995, 'spop3,pop-3s'),
			('pptp', 'Point-to-Point Tunneling Protocol', 'tcp', 1723, 1723, 'pptpd'),
			('smtp', 'Simple Mail Transfer Protocol', 'tcp', 25, 25, 'mail'),
			('smtps', 'Simple Mail Transfer Protocol over SSL', 'tcp', 465, 465, 'ssmtp,smail,mails'),
			('http', 'Hypertext Transfer Protocol', 'tcp', 80, 80, 'www,www-http,http-www'),
			('https', 'Hypertext Transfer Protocol over SSL', 'tcp', 443, 443, 'www-https,https-www'),
			('ircd', 'Internet Relay Chat', 'tcp', 6667, 6667, None),
			('ssh', 'Secure Shell', 'tcp', 22, 22, None),
			('telnet', 'Telnet Service', 'tcp', 23, 23, 'telnetd'),
			('kerberos', 'Kerberos Auth Service', 'tcp', 88, 88, 'kerberos5,krb5'),
			('kerberos', 'Kerberos Auth Service', 'udp', 88, 88, 'kerberos5, krb5'),
			('ldap', 'Lightweight Directory Access Protocol', 'tcp', 389, 389, 'nds'),
			('ldaps', 'Lightweight Directory Access Protocol over SSL', 'tcp', 636, 636, 'sldap,ndss,snds'),
			('kerberos-master', 'Kerberos Master Auth Service', 'udp', 88, 88, 'kerberos5-master,krb5-master'),
			('kerberos-adm', 'Kerberos Administration Service', 'tcp', 749, 749, 'kerberos5-adm,krb5-adm'),
			('kpasswd', 'Kerberos Master Passwd Service', 'udp', 464, 464, 'kpwd'),
			('kerberos-iv', 'Kerberos IV Auth Service', 'udp', 750, 750, 'kerberos4,kdc,krb4'),
			('timed', 'Time Service', 'udp', 525, 525, 'timeserver'),
			('ntp', 'Network Time Protocol', 'udp', 123, 123, 'sntp'),
			('netbios-ns', 'NetBIOS Name Service', 'tcp', 137, 137, None),
			('netbios-ns', 'NetBIOS Name Service', 'udp', 137, 137, None),
			('netbios-dgm', 'NetBIOS Datagram Service', 'tcp', 138, 138, None),
			('netbios-dgm', 'NetBIOS Datagram Service', 'udp', 138, 138, None),
			('netbios-ssn', 'NetBIOS Session Service', 'tcp', 139, 139, None),
			('netbios-ssn', 'NetBIOS Session Service', 'udp', 139, 139, None),
			('microsoft-ds', 'Microsoft DS', 'tcp', 445, 445, 'Microsoft-DS'),
			('imsp', 'Interactive Mail Support Protocol', 'tcp', 406, 406, None),
			('epmap', 'DCE Endpoint Resolution Protocol', 'tcp', 135, 135, 'loc-srv'),
			('epmap', 'DCE Endpoint Resolution Protocol', 'udp', 135, 135, 'loc-srv'),
			('mysql', 'MySQL RDBMS Service', 'tcp', 3306, 3306, None),
			('postgresql', 'PostgreSQL RDBMS Service', 'tcp', 5432, 5432, None),
			('kftp', 'Kerberos V File Transfer Protocol', 'tcp', 6621, 6621, None),
			('kftp-data', 'Kerberos V File Transfer Protocol Data Stream', 'tcp', 6620, 6620, None),
			('ktelnet', 'Kerberos V Telnet Service', 'tcp', 6623, 6623, None),
			('soap-http', 'SOAP HTTP Service', 'tcp', 7627, 7627, 'http-soap'),
			('bootps', 'Bootstrap Protocol Server', 'udp', 67, 67, None),
			('tftp', 'Trivial File Transfer Protocol', 'udp', 69, 69, None),
			('rtelnet', 'Remote Telnet Service', 'tcp', 107, 107, None),
			('rtelnet', 'Remote Telnet Service', 'udp', 107, 107, None),
			('jabber', 'Jabber IM Service', 'tcp', 5269, 5269, None),
			('xmpp-server', 'Jabber XMPP Protocol Server', 'tcp', 5269, 5269, None),
			('xmpp-client', 'Jabber XMPP Protocol Client', 'tcp', 5222, 5222, None),
			('xmpp-client-ssl', 'Jabber XMPP Protocol Client over SSL', 'tcp', 5223, 5223, None),
			('radius', 'RADIUS Service', 'tcp', 1812, 1812, None),
			('radius', 'RADIUS Service', 'udp', 1812, 1812, None),
			('radius-acct', 'RADIUS Accounting Service', 'tcp', 1813, 1813, 'radacct'),
			('radius-acct', 'RADIUS Accounting Service', 'udp', 1813, 1813, 'radacct'),
			('radius-dynauth', 'RADIUS Dynamic Authorization', 'tcp', 3799, 3799, None),
			('radius-dynauth', 'RADIUS Dynamic Authorization', 'udp', 3799, 3799, None),
			('tacacs', 'Login Host Protocol (TACACS)', 'tcp', 49, 49, None),
			('tacacs', 'Login Host Protocol (TACACS)', 'udp', 49, 49, None),
			('tacacs-ds', 'TACACS Database Service', 'tcp', 65, 65, None),
			('tacacs-ds', 'TACACS Database Service', 'udp', 65, 65, None),
			('finger', 'Finger Service', 'tcp', 79, 79, 'fingerd'),
			('pop2', 'Post Office Protocol version 2', 'tcp', 109, 109, 'pop-2,postoffice'),
			('sunrpc', 'SUN Remote Procedure Call', 'tcp', 111, 111, 'portmapper'),
			('sunrpc', 'SUN Remote Procedure Call', 'udp', 111, 111, 'portmapper'),
			('auth', 'Authentication Service', 'tcp', 113, 113, 'authentication,tap,ident'),
			('snmp', 'Simple Network Management Protocol', 'tcp', 161, 161, None),
			('snmp', 'Simple Network Management Protocol', 'udp', 161, 161, None),
			('snmptrap', 'SNMP Trap Port', 'tcp', 162, 162, 'snmp-trap'),
			('snmptrap', 'SNMP Trap Port', 'udp', 162, 162, 'snmp-trap'),
			('bgp', 'Border Gateway Protocol', 'tcp', 179, 179, None),
			('bgp', 'Border Gateway Protocol', 'udp', 179, 179, None),
			('bgp', 'Border Gateway Protocol', 'sctp', 179, 179, None),
			('smux', 'SNMP Multiplexing', 'tcp', 199, 199, None),
			('smux', 'SNMP Multiplexing', 'udp', 199, 199, None),
			('imap3', 'Interactive Mail Access Protocol version 3', 'tcp', 220, 220, None),
			('imap3', 'Interactive Mail Access Protocol version 3', 'udp', 220, 220, None),
			('snpp', 'Simple Network Paging Protocol', 'tcp', 444, 444, None),
			('who', 'Who is Logged In Service', 'udp', 513, 513, 'whod'),
			('syslog', 'System Logging Service', 'udp', 514, 514, 'syslogd'),
			('utime', 'UNIX Time Service', 'tcp', 519, 519, 'unixtime'),
			('utime', 'UNIX Time Service', 'udp', 519, 519, 'unixtime'),
			('klogin', 'Kerberos V Remote Login Service', 'tcp', 543, 543, 'krlogin'),
			('klogin', 'Kerberos V Remote Login Service', 'udp', 543, 543, 'krlogin'),
			('kshell', 'Kerberos V Remote Commands Service', 'tcp', 544, 544, 'krcmd'),
			('kshell', 'Kerberos V Remote Commands Service', 'udp', 544, 544, 'krcmd'),
			('ipp', 'Internet Printing Protocol', 'tcp', 631, 631, None),
			('ipp', 'Internet Printing Protocol', 'udp', 631, 631, None),
			('rsync', 'RSYNC Service', 'tcp', 873, 873, None),
			('rsync', 'RSYNC Service', 'udp', 873, 873, None),
			('ftps', 'File Transfer Protocol over SSL', 'tcp', 990, 990, None),
			('ftps-data', 'File Transfer Protocol Data Stream over SSL', 'tcp', 989, 989, None),
			('telnets', 'Telnet Service over SSL', 'tcp', 992, 992, 'stelnet'),
			('socks', 'Socks Proxy Server', 'tcp', 1080, 1080, None),
			('socks', 'Socks Proxy Server', 'udp', 1080, 1080, None),
			('openvpn', 'OpenVPN Service', 'tcp', 1194, 1194, 'open-vpn'),
			('openvpn', 'OpenVPN Service', 'udp', 1194, 1194, 'open-vpn'),
			('wins', 'Windows Internet Name Service', 'tcp', 1512, 1512, None),
			('wins', 'Windows Internet Name Service', 'udp', 1512, 1512, None),
			('l2tp', 'Level 2 Tunneling Protocol', 'tcp', 1701, 1701, 'l2f'),
			('l2tp', 'Level 2 Tunneling Protocol', 'udp', 1701, 1701, 'l2f'),
			('mysql-im', 'MySQL Instance Manager Service', 'tcp', 2273, 2273, 'mysqlim'),
			('icpv2', 'Internet Cache Protocol', 'tcp', 3130, 3130, 'icp'),
			('icpv2', 'Internet Cache Protocol', 'udp', 3130, 3130, 'icp'),
			('daap', 'Digital Audio Access Protocol', 'tcp', 3689, 3689, None),
			('daap', 'Digital Audio Access Protocol', 'udp', 3689, 3689, None),
			('xgrid', 'Mac OS X Server Xgrid', 'tcp', 4111, 4111, None),
			('xgrid', 'Mac OS X Server Xgrid', 'udp', 4111, 4111, None),
			('mdns', 'Multicast DNS', 'udp', 5353, 5353, None),
			('mdnsresponder', 'Multicast DNS Responder IPC', 'udp', 5354, 5354, None)
		)
		for t in stypes:
			st = ServiceType()
			st.abbreviation = t[0]
			st.name = t[1]
			st.protocol = ServiceProtocol.from_string(t[2])
			st.start_port = t[3]
			st.end_port = t[4]
			if t[5]:
				st.alias = t[5]
			sess.add(st)

	def get_css(self, request):
		return (
			'netprofile_hosts:static/css/main.css',
		)

	@property
	def name(self):
		return _('Hosts')

