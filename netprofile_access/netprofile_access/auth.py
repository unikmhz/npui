#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Access module - Models
# © Copyright 2013-2015 Alex 'Unik' Unigovsky
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
	NewResponse,
	ContextFound
)
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.settings import asbool
from sqlalchemy.orm.exc import NoResultFound

from netprofile.db.connection import DBSession
from netprofile.db.clauses import (
	SetVariable,
	SetVariables
)

def get_user(request):
	sess = DBSession()
	userid = unauthenticated_userid(request)

	if userid is not None:
		from .models import AccessEntity
		try:
			return sess.query(AccessEntity).filter(
				AccessEntity.nick == userid
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
		'accesslogin' : '[ACCESS:%s]' % (user.nick,) if user else '[ACCESS:GUEST]'
	}
	try:
		sess.execute(SetVariables(**db_vars))
	except NotImplementedError:
		for vname in db_vars:
			sess.execute(SetVariable(vname, db_vars[vname]))

def _new_response(event):
	request = event.request
	settings = request.registry.settings
	response = event.response
	# TODO: add static URL if set
	csp = 'default-src \'self\' www.google.com; style-src \'self\' www.google.com \'unsafe-inline\''
	if request.debug_enabled:
		csp += '; script-src \'self\' www.google.com \'unsafe-inline\''
	response.headerlist.extend((
		('Content-Security-Policy', csp),
		('X-Content-Type-Options', 'nosniff')
	))
	if 'X-Frame-Options' not in response.headers:
		response.headerlist.append(('X-Frame-Options', 'DENY'))
	if asbool(settings.get('netprofile.http.sts.enabled', False)):
		try:
			max_age = int(settings.get('netprofile.http.sts.max_age', 604800))
		except (TypeError, ValueError):
			max_age = 604800
		sts_chunks = [ 'max-age=' + str(max_age) ]
		if asbool(settings.get('netprofile.http.sts.include_subdomains', False)):
			sts_chunks.append('includeSubDomains')
		if asbool(settings.get('netprofile.http.sts.preload', False)):
			sts_chunks.append('preload')
		response.headerlist.append(('Strict-Transport-Security', '; '.join(sts_chunks)))

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	config.add_request_method(get_user, str('user'), reify=True)
	config.add_request_method(get_acls, str('acls'), reify=True)

	settings = config.registry.settings

	authn_policy = SessionAuthenticationPolicy()
	authz_policy = ACLAuthorizationPolicy()

	config.set_authorization_policy(authz_policy)
	config.set_authentication_policy(authn_policy)

	config.add_subscriber(_new_response, NewResponse)
	config.add_subscriber(_auth_to_db, ContextFound)

