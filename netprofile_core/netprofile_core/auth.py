from pyramid.security import (
	Allow,
	Deny,
	Everyone,
	Authenticated,
	unauthenticated_userid
)
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy.orm.exc import NoResultFound

from netprofile.db.connection import DBSession
from .models import (
	Privilege,
	User,
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
		q = sess.query(Privilege).all()
		for priv in q:
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

def find_princs(userid, request):
	sess = DBSession()

	user = request.user
	if user.login == userid:
		return []
	try:
		user = sess.query(User).filter(User.state == UserState.active).filter(User.enabled == True).filter(User.login == userid).one()
	except NoResultFound:
		return None
	return []

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	config.set_request_property(get_user, 'user', reify=True)
	config.set_request_property(get_acls, 'acls', reify=True)

	authn_policy = SessionAuthenticationPolicy(callback=find_princs)
	authz_policy = ACLAuthorizationPolicy()

	config.set_authorization_policy(authz_policy)
	config.set_authentication_policy(authn_policy)

