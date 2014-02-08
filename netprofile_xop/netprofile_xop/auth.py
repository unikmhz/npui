#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: XOP module - Models
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

from pyramid.security import (
	Allow,
	Deny,
	Everyone,
	Authenticated,
	unauthenticated_userid
)
from pyramid.events import (
	NewRequest,
	ContextFound
)
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from sqlalchemy.orm.exc import NoResultFound

from netprofile.db.connection import DBSession
from netprofile.db.clauses import SetVariable

from netprofile.common.auth import (
	DigestAuthenticationPolicy,
	PluginAuthenticationPolicy
)
from .models import ExternalOperationProvider

from netprofile_core.models import User
from netprofile_entities.models import Entity
from netprofile_rates.models import RateModifierType
from netprofile_dialup.models import IPPool
from netprofile_hosts.models import Host
from netprofile_networks.models import Network
from netprofile_ipaddresses.models import IPv4Address
from netprofile_access.models import AccessEntity
from netprofile_stashes.models import (
	StashIOType,
	Stash
)

import binascii
import hashlib

#from zope.interface import implements
from zope.interface import implementer

from pyramid.security import Everyone
from pyramid.security import Authenticated

def _get_credentials(request):
	if 'login' in request.POST and 'password' in request.POST:
		return {'login':request.POST.get('login', ''), 'password':request.POST.get('password', '')}
	return None

def _parse_authorization(request, secret, realm):
	authz = request.authorization
	if (not authz) or (len(authz) != 2) or (authz[0] != 'Digest'):
		_add_www_authenticate(request, secret, realm)
		return None
	params = authz[1]
	if 'algorithm' not in params:
		params['algorithm'] = 'MD5'
	for required in ('username', 'realm', 'nonce', 'uri', 'response', 'cnonce', 'nc', 'opaque'):
		if (required not in params) or ((required == 'opaque') and (params['opaque'] != 'NPDIGEST')):
			_add_www_authenticate(request, secret, realm)
			return None
	return params

def _get_basicauth_credentials(request):
	authorization = request.authorization
	try:
		authmeth, auth = authorization.split(' ', 1)
	except ValueError: # not enough values to unpack
		return None
	if authmeth.lower() == 'basic':
		try:
			auth = auth.strip().decode('base64')
		except binascii.Error: # can't decode
			return None
		try:
			login, password = auth.split(':', 1)
		except ValueError: # not enough values to unpack
			return None
		return {'login':login, 'password':password}

	return None

def find_princs(userid, request):
	sess = DBSession()

	user = request.user
	if user and (user.authuser == userid):
		return []
	try:
		user = sess.query(ExternalOperationProvider).filter(
			ExternalOperationProvider.enabled == True,
			ExternalOperationProvider.auth == userid
		).one()
	except NoResultFound:
		return None
	return []

@implementer(IAuthenticationPolicy)
class BasicAuthenticationXOPPolicy(object):

	def __init__(self, login, password, realm='Realm'):
		self.login = login
		self.password = password
		self.realm = realm

	def authenticated_userid(self, request):
		credentials = _get_basicauth_credentials(request)
		if credentials is None:
			return None
		if credentials['user'] == self.user and credentials['password']  == self.password: 
			return  credentials['user']

	def effective_principals(self, request):
		effective_principals = [Everyone]
		credentials = _get_basicauth_credentials(request)
		if credentials is None:
			return effective_principals
		userid = credentials['login']
		groups = ['group']
		effective_principals.append(Authenticated)
		effective_principals.append(userid)
		effective_principals.extend(groups)
		return effective_principals

	def unauthenticated_userid(self, request):
		creds = _get_basicauth_credentials(request)
		if creds is not None:
			return creds['login']
		return None

	def remember(self, request, principal, **kw):
		return []

	def forget(self, request):
		return [('WWW-Authenticate: Basic realm="%s"' % self.realm)]


@implementer(IAuthenticationPolicy)
class HashAuthenticationXOPPolicy(object):

	def __init__(self, login, password, hash):
		self.login = login
		if(hash == 'md5'):
			self.password = hashlib.md5(password).encode()
		elif(hash == 'sha1'):
			self.password = hashlib.sha1(password).encode()

	def authenticated_userid(self, request):
		credentials = _get_credentials(request)
		if credentials is None:
			return None
		if credentials['user'] == self.user and credentials['password']  == self.password: 
			return  credentials['user']

	def effective_principals(self, request):
		effective_principals = [Everyone]
		credentials = _get_credentials(request)
		if credentials is None:
			return effective_principals
		userid = credentials['login']
		groups = ['group']
		effective_principals.append(Authenticated)
		effective_principals.append(userid)
		effective_principals.extend(groups)
		return effective_principals

	def unauthenticated_userid(self, request):
		creds = _get_credentials(request)
		if creds is not None:
			return creds['login']
		return None

	def remember(self, request, principal, **kw):
		return []

	def forget(self, request):
		return []

def get_user(request):
	sess = DBSession()
	userid = unauthenticated_userid(request)

	if userid is not None:
		try:
			return sess.query(ExternalOperationProvider).filter(
				ExternalOperationProvider.authuser == userid
			).one()
		except NoResultFound:
			return None

def get_acls(request):
	return [(Allow, Authenticated, 'USAGE')]

def _auth_to_db(event):
	request = event.request

	if not request.matched_route:
		return
	rname = request.matched_route.name
	if rname[0] == '_':
		return

	sess = DBSession()
	user = request.user

	sess.execute(SetVariable('accessuid', 0))
	sess.execute(SetVariable('accessgid', 0))
	if user:
		sess.execute(SetVariable('accesslogin', '[XOP:%s]' % user.name))
	else:
		sess.execute(SetVariable('accesslogin', '[XOP:GUEST]'))

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	config.add_request_method(get_user, str('user'), reify=True)
	config.add_request_method(get_acls, str('acls'), reify=True)

	settings = config.registry.settings

	sess = DBSession()
	sess.query(ExternalOperationProvider)

	opts = dict()

	for xopp in sess.query(ExternalOperationProvider):
		if(xopp.authmethod == ExternalOperationProviderAuthMethod.http):
			opts.update ({ 
				'/' + xopp.uri : BasicAuthenticationXOPPolicy(
					xopp.authuser,
					xopp.authpass,
					settings.get('netprofile.auth.http_realm', 'NetProfile UI')
				)
			})
		elif(xopp.authmethod == ExternalOperationProviderAuthMethod.md5):
			opts.update ({ 
				'/' + xopp.uri : HashAuthenticationXOPPolicy(xopp.authuser, xopp.authpass, 'md5')
			})
		elif(xopp.authmethod == ExternalOperationProviderAuthMethod.sha1):
			opts.update ({ 
				'/' + xopp.uri : HashAuthenticationXOPPolicy(xopp.authuser, xopp.authpass, 'sha1')
			})
			
	authn_policy = PluginAuthenticationPolicy(
		SessionAuthenticationPolicy(callback=find_princs),
		opts
	)
	authz_policy = ACLAuthorizationPolicy()

	config.set_authorization_policy(authz_policy)
	config.set_authentication_policy(authn_policy)

	config.add_subscriber(_auth_to_db, ContextFound)

