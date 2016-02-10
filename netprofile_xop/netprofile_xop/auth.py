#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: XOP module - Authentication
# © Copyright 2014 Alex 'Unik' Unigovsky
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
from pyramid.events import ContextFound
from pyramid.authentication import (
	BasicAuthAuthenticationPolicy,
	CallbackAuthenticationPolicy,
	SessionAuthenticationPolicy
)
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from sqlalchemy.orm.exc import NoResultFound

from netprofile.db.connection import DBSession
from netprofile.db.clauses import (
	SetVariable,
	SetVariables
)

from netprofile.common.auth import PluginAuthenticationPolicy

import binascii
import hashlib

from zope.interface import implementer

from pyramid.security import (
	Authenticated,
	Everyone
)

from .models import (
	ExternalOperationProvider,
	ExternalOperationProviderAuthMethod
)

def find_princs(userid, request):
	sess = DBSession()

	user = request.user
	if user and (user.authentication_username == userid):
		return []
	try:
		user = sess.query(ExternalOperationProvider).filter(
			ExternalOperationProvider.enabled == True,
			ExternalOperationProvider.authentication_username == userid
		).one()
	except NoResultFound:
		return None
	return []

@implementer(IAuthenticationPolicy)
class XOPBasicAuthenticationPolicy(BasicAuthAuthenticationPolicy):
	def __init__(self, username, password, realm='Realm', debug=False):
		super(XOPBasicAuthenticationPolicy, self).__init__(self._std_check, realm, debug)
		self.username = username
		self.password = password

	def _std_check(username, password, request):
		if username != self.username:
			return None
		if password != self.password:
			return None
		return []

@implementer(IAuthenticationPolicy)
class XOPHashAuthenticationPolicy(CallbackAuthenticationPolicy):
	def __init__(self, username, password, htype):
		self.username = username
		self.password = password
		self.hash_type = htype

	def _get_credentials(request):
		if 'user' in request.params and 'password' in request.params:
			cred = {
				'user' : request.params.get('user'),
				'pass' : request.params.get('pass')
			}
			if 'salt' in request.params:
				cred['salt'] = request.params.get('salt')
			return cred

	def unauthenticated_userid(self, request):
		creds = self._get_credentials(request)
		if creds:
			return creds['user']

	def remember(self, request, principal, **kw):
		return []

	def forget(self, request):
		return []

	def callback(self, username, request):
		creds = self._get_credentials(request)
		if creds:
			if username != creds['user']:
				return None
			password = creds.get('pass', '')
			salt = creds.get('salt', '')
			ctx = hashlib.new(self.hash_type)
			ctx.update(salt.encode())
			ctx.update(password.encode())
			if ctx.hexdigest() == password:
				return []

@implementer(IAuthenticationPolicy)
class XOPNoneAuthenticationPolicy(CallbackAuthenticationPolicy):
	def __init__(self, username):
		self.username = username

	def unauthenticated_userid(self, request):
		return self.username

	def remember(self, request, principal, **kw):
		return []

	def forget(self, request):
		return []

	def callback(self, username, request):
		return []


def get_user(request):
	sess = DBSession()
	userid = unauthenticated_userid(request)

	if userid is not None:
		try:
			return sess.query(ExternalOperationProvider).filter(
				ExternalOperationProvider.authentication_username == userid
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

	db_vars = {
		'accessuid'   : 0,
		'accessgid'   : 0,
		'accesslogin' : '[XOP:%s]' % (user.name,) if user else '[XOP:GUEST]'
	}
	try:
		sess.execute(SetVariables(**db_vars))
	except NotImplementedError:
		for vname in db_vars:
			sess.execute(SetVariable(vname, db_vars[vname]))

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	config.add_request_method(get_user, str('user'), reify=True)
	config.add_request_method(get_acls, str('acls'), reify=True)

	settings = config.registry.settings

	sess = DBSession()
	opts = dict()

	for xopp in sess.query(ExternalOperationProvider):
		uri = '/' + xopp.uri
		if(xopp.authentication_method == ExternalOperationProviderAuthMethod.http):
			opts[uri] = XOPBasicAuthenticationPolicy(
					xopp.authentication_username,
					xopp.authentication_password,
					settings.get('netprofile.auth.http_realm', 'NetProfile XOP')
				)
		elif(xopp.authentication_method == ExternalOperationProviderAuthMethod.md5):
			opts[uri] = XOPHashAuthenticationPolicy(xopp.authentication_username, xopp.authentication_password, 'md5')
		elif(xopp.authentication_method == ExternalOperationProviderAuthMethod.sha1):
			opts[uri] = XOPHashAuthenticationPolicy(xopp.authentication_username, xopp.authentication_password, 'sha1')
		elif(xopp.authentication_method is None):
			opts[uri] = XOPNoneAuthenticationPolicy(xopp.short_name)
			
	authn_policy = PluginAuthenticationPolicy(
		SessionAuthenticationPolicy(callback=find_princs),
		opts
	)
	authz_policy = ACLAuthorizationPolicy()

	config.set_authorization_policy(authz_policy)
	config.set_authentication_policy(authn_policy)

	config.add_subscriber(_auth_to_db, ContextFound)

