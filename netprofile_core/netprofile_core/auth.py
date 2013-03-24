#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
	ContextFound,
	subscriber
)
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy import (
	and_,
	text
)
from sqlalchemy.orm.exc import NoResultFound

from netprofile.db.connection import DBSession
from .models import (
	Privilege,
	User,
	UserSetting,
	UserSettingType,
	UserState
)

def get_user(request):
	sess = DBSession()
	userid = unauthenticated_userid(request)

	if userid is not None:
		try:
			return sess.query(User).filter(User.state == UserState.active).filter(User.enabled == True).filter(User.login == userid).one()
		except NoResultFound:
			return None

def get_acls(request):
	# FIXME: implement ACL cache invalidation
	if 'auth.acls' in request.session:
		return request.session['auth.acls']
	ret = [(Allow, Authenticated, 'USAGE')]
	user = request.user
	if user is None:
		sess = DBSession()
		for priv in sess.query(Privilege):
			if priv.guest_value:
				right = Allow
			else:
				right = Deny
			ret.append((right, Everyone, priv.code))
		request.session['auth.acls'] = ret
		return ret
	for perm, val in user.flat_privileges.items():
		if val:
			right = Allow
		else:
			right = Deny
		ret.append((right, user.login, perm))
	request.session['auth.acls'] = ret
	return ret

def get_settings(request):
	# FIXME: implement settings cache invalidation
	if 'auth.settings' in request.session:
		return request.session['auth.settings']
	sess = DBSession()
	user = request.user
	ret = {}
	if user is None:
		for ust in sess.query(UserSettingType):
			ret[ust.name] = ust.parse_param(ust.default)
	else:
		for (ust, us) in sess \
			.query(UserSettingType, UserSetting) \
			.outerjoin(UserSetting, and_(
				UserSettingType.id == UserSetting.type_id,
				UserSetting.user == request.user
		)):
			if us and (us.value is not None):
				ret[ust.name] = ust.parse_param(us.value)
			else:
				ret[ust.name] = ust.parse_param(ust.default)
	request.session['auth.settings'] = ret
	return ret

def find_princs(userid, request):
	sess = DBSession()

	user = request.user
	if user and (user.login == userid):
		return []
	try:
		user = sess.query(User).filter(User.state == UserState.active).filter(User.enabled == True).filter(User.login == userid).one()
	except NoResultFound:
		return None
	return []

@subscriber(ContextFound)
def auth_to_db(event):
	request = event.request

	rname = request.matched_route.name
	if rname[0] == '_':
		return

	sess = DBSession()
	user = request.user

	if user:
		sess.execute('SET @accessuid = :uid', { 'uid' : user.id })
		sess.execute('SET @accessgid = :gid', { 'gid' : user.group_id })
		sess.execute('SET @accesslogin = :login', { 'login' : user.login })
	else:
		sess.execute('SET @accessuid = 0')
		sess.execute('SET @accessgid = 0')
		sess.execute('SET @accesslogin = \'[GUEST]\'')

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	config.add_request_method(get_user, str('user'), reify=True)
	config.add_request_method(get_acls, str('acls'), reify=True)
	config.add_request_method(get_settings, str('settings'), reify=True)

	authn_policy = SessionAuthenticationPolicy(callback=find_princs)
	authz_policy = ACLAuthorizationPolicy()

	config.set_authorization_policy(authz_policy)
	config.set_authentication_policy(authn_policy)

