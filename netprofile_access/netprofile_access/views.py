#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Access module - Views
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

import datetime, os, random, re, string, hashlib
import json

from rauth import OAuth2Service, OAuth1Service
from rauth.utils import parse_utf8_qsl

from sqlalchemy import func
from sqlalchemy.orm import joinedload
from pyramid.view import (
	notfound_view_config,
	forbidden_view_config,
	view_config
)
from pyramid.security import (
	authenticated_userid,
	forget,
	remember
)
from pyramid.httpexceptions import (
	HTTPForbidden,
	HTTPFound,
	HTTPNotFound,
	HTTPSeeOther
)
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer,
	get_locale_name
)
from pyramid.response import (
	FileResponse,
	Response
)
from pyramid.settings import asbool
from pyramid.renderers import render
from pyramid_mailer import get_mailer
from pyramid_mailer.message import (
	Attachment,
	Message
)
from babel.core import Locale
from netprofile import locale_neg
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from netprofile_core.models import File
from netprofile_entities.models import (
	Entity,
	LegalEntity,
	PhysicalEntity
)
from netprofile_stashes.models import Stash
from netprofile_rates.models import Rate

from .models import (
	AccessEntity,
	AccessEntityLink,
	AccessState
)
from .recaptcha import verify_recaptcha

_ = TranslationStringFactory('netprofile_access')

_re_login = re.compile(r'^[\w\d._-]+$')
_re_email = re.compile(r'^[-.\w]+@(?:[\w\d-]{2,}\.)+\w{2,6}$')

@view_config(route_name='access.cl.home', renderer='netprofile_access:templates/client_home.mak', permission='USAGE')
def client_home(request):
	tpldef = {}
	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.home', tpldef, request)
	return tpldef

@notfound_view_config(vhost='client', renderer='netprofile_access:templates/client_error.mak')
def client_notfound(request):
	loc = get_localizer(request)
	request.response.status_code = 404
	tpldef = {
		'error' : loc.translate(_('Page Not Found'))
	}
	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.error', tpldef, request)
	return tpldef

@forbidden_view_config(vhost='client', renderer='netprofile_access:templates/client_error.mak')
def client_forbidden(request):
	loc = get_localizer(request)
	if not authenticated_userid(request):
		request.session.flash({
			'class' : 'warning',
			'text'  : loc.translate(_('You need to log in to access this page'))
		})
		return HTTPSeeOther(location=request.route_url('access.cl.login'))
	request.response.status_code = 403
	tpldef = {
		'error' : loc.translate(_('Access Denied'))
	}
	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.error', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.chpass', renderer='netprofile_access:templates/client_chpass.mak', permission='USAGE')
def client_chpass(request):
	cfg = request.registry.settings
	loc = get_localizer(request)
	min_pwd_len = int(cfg.get('netprofile.client.registration.min_password_length', 8))
	errors = {}
	if 'submit' in request.POST:
		csrf = request.POST.get('csrf', '')
		oldpass = request.POST.get('oldpass', '')
		passwd = request.POST.get('pass', '')
		passwd2 = request.POST.get('pass2', '')
		if csrf != request.get_csrf():
			errors['csrf'] = _('Error submitting form')
		else:
			l = len(passwd)
			if l < min_pwd_len:
				errors['pass'] = _('Password is too short')
			elif l > 254:
				errors['pass'] = _('Password is too long')
			if passwd != passwd2:
				errors['pass2'] = _('Passwords do not match')
			if request.user.password != oldpass:
				errors['oldpass'] = _('Wrong password')
		if len(errors) == 0:
			request.user.password = passwd
			request.session.flash({
				'text' : loc.translate(_('Password successfully changed'))
			})
			return HTTPSeeOther(location=request.route_url('access.cl.home'))
	tpldef = {
		'errors'      : {err: loc.translate(errors[err]) for err in errors},
		'min_pwd_len' : min_pwd_len
	}
	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.chpass', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.upload', xhr=True, request_method='GET', renderer='json', permission='USAGE')
def client_file_list(request):
	csrf = request.GET.get('csrf', '')
	mode = request.GET.get('mode', '')
	if not mode:
		raise HTTPForbidden('Invalid upload use')
	if csrf != request.get_csrf():
		raise HTTPForbidden('Error uploading file')
	sess = DBSession()
	tpldef = []
	request.run_hook('access.cl.file_list', mode, request, sess, tpldef)
	tpldef = { 'files' : tpldef }
	request.run_hook('access.cl.tpldef.upload', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.upload', xhr=True, request_method='POST', renderer='json', permission='USAGE')
def client_upload(request):
	csrf = request.POST.get('csrf', '')
	mode = request.POST.get('mode', '')
	if not mode:
		raise HTTPForbidden('Invalid upload use')
	if csrf != request.get_csrf():
		raise HTTPForbidden('Error uploading file')
	sess = DBSession()
	# FIXME: add folder cfg
	tpldef = []
	for fo in request.POST.getall('files'):
		obj = File()
		if fo.filename:
			obj.name = obj.filename = fo.filename
		sess.add(obj)
		obj.set_from_file(fo.file, None, sess)
		signal = request.run_hook('access.cl.upload', obj, mode, request, sess, tpldef)
		if True not in signal:
			tpldef.append({
				'name'  : obj.filename,
				'size'  : obj.size,
				'error' : _('Error uploading file')
			})
			sess.delete(obj)
	tpldef = { 'files' : tpldef }
	request.run_hook('access.cl.tpldef.upload', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.download', request_method='GET', permission='USAGE')
def client_download(request):
	if ('mode' not in request.matchdict) or ('id' not in request.matchdict):
		raise HTTPForbidden('Invalid download link')
	mode = request.matchdict['mode']
	try:
		objid = int(request.matchdict['id'])
	except ValueError:
		raise HTTPForbidden('Invalid download link')
	sess = DBSession()
	ret = request.run_hook('access.cl.download', mode, objid, request, sess)
	for r in ret:
		if isinstance(r, File):
			return r.get_response(request)
	raise HTTPForbidden('Invalid download link')

@view_config(route_name='access.cl.download', xhr=True, request_method='DELETE', renderer='json', permission='USAGE')
def client_delete(request):
	if ('mode' not in request.matchdict) or ('id' not in request.matchdict):
		return False
	mode = request.matchdict['mode']
	try:
		objid = int(request.matchdict['id'])
	except ValueError:
		return False
	sess = DBSession()
	ret = request.run_hook('access.cl.download', mode, objid, request, sess)
	for r in ret:
		if isinstance(r, File):
			sess.delete(r)
			return True
	return False

@view_config(route_name='access.cl.login', renderer='netprofile_access:templates/client_login.mak')
def client_login(request):
	nxt = request.route_url('access.cl.home')
	if authenticated_userid(request):
		return HTTPSeeOther(location=nxt)
	login = ''
	did_fail = False
	cur_locale = locale_neg(request)
	cfg = request.registry.settings
	comb_js = asbool(cfg.get('netprofile.client.combine_js', False))
	can_reg = asbool(cfg.get('netprofile.client.registration.enabled', False))
	can_recover = asbool(cfg.get('netprofile.client.password_recovery.enabled', False))
	maillogin = asbool(cfg.get('netprofile.client.email_as_username', False))
	can_use_socialnetworks = asbool(cfg.get('netprofile.client.registration.social', False))

	login_providers = {'facebook':'http://facebook.com',
					   'google'	 :'http://google.com',
					   'twitter' :'http://twitter.com' 
					   }

	if 'submit' in request.POST:
		csrf = request.POST.get('csrf', '')
		login = request.POST.get('user', '')
		passwd = request.POST.get('pass', '')

		if (csrf == request.get_csrf()) and login:
			sess = DBSession()
			q = sess.query(AccessEntity).filter(AccessEntity.nick == login, AccessEntity.access_state != AccessState.block_inactive.value)
			for user in q:
				if user.password == passwd:
					headers = remember(request, login)
					return HTTPSeeOther(location=nxt, headers=headers)
		did_fail = True

	tpldef = {
		'login'          : login,
		'failed'         : did_fail,
		'can_reg'        : can_reg,
		'can_usesocial'  : can_use_socialnetworks,
		'login_providers': login_providers,
		'can_recover'    : can_recover,
		'cur_loc'        : cur_locale,
		'comb_js'        : comb_js
	}
	request.run_hook('access.cl.tpldef.login', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.oauthwrapper', request_method='GET')
def client_oauth_wrapper(request):
	auth_provider = request.GET.get('prov', None)
	redirect_uri = request.route_url('access.cl.home')

	if auth_provider == 'facebook':
		redirect_uri = request.route_url('access.cl.oauthfacebook')
	elif auth_provider == 'google':
		redirect_uri = request.route_url('access.cl.oauthgoogle')
	elif auth_provider == 'twitter':
		csrf = request.GET.get('csrf', None)
		email = request.GET.get('twitterEmail', None)
		if email and csrf == request.get_csrf():
			return HTTPFound(location=request.route_url('access.cl.oauthtwitter', email=email))

	return HTTPSeeOther(redirect_uri)

@view_config(route_name='access.cl.oauthtwitter', request_method='GET')
def client_oauth_twitter(request):
	if authenticated_userid(request):
		return HTTPSeeOther(location=request.route_url('access.cl.home'))

	cfg = request.registry.settings
	loc = get_localizer(request)
	req_session = request.session

	min_pwd_len = int(cfg.get('netprofile.client.registration.min_password_length', 8))
	auth_provider = 'twitter'



	email =  request.matchdict['email']
	redirect_uri = request.route_url('access.cl.oauthtwitter', email=email)

	reg_params = {
		'email':email,
		'username':None,
		'password':None,
		'givenname':None,
		'familyname':None,
		}

	TWITTER_APP_ID = cfg.get('netprofile.client.TWITTER_APP_ID', False)
	TWITTER_APP_SECRET = cfg.get('netprofile.client.TWITTER_APP_SECRET', False)

	twitter = OAuth1Service(
		consumer_key=TWITTER_APP_ID,
		consumer_secret=TWITTER_APP_SECRET,
		name='twitter',
		authorize_url='https://api.twitter.com/oauth/authorize',
		access_token_url='https://api.twitter.com/oauth/access_token',
		request_token_url='https://api.twitter.com/oauth/request_token',
		base_url='https://api.twitter.com/1.1/')

	if TWITTER_APP_ID and TWITTER_APP_SECRET:
		auth_token = request.GET.get('oauth_token', False)
		auth_verifier = request.GET.get('oauth_verifier', False)

		if not auth_token and not auth_verifier:
			params = {
				'oauth_callback': redirect_uri,
				}

			authorize_url = twitter.get_raw_request_token(params=params)

			data = parse_utf8_qsl(authorize_url.content)

			# should pass callback_url
			# and get something like http://netprofile.ru/?oauth_token=1jMq4YD5cKEgRrOjoRae3xdfHJaoQRPf&oauth_verifier=bpOPZ1CYVUGtNs8nTFihwBv6KWhJzV1C
			# http://stackoverflow.com/questions/17512572/rauth-flask-how-to-login-via-twitter
		    #it works

			req_session['twitter_oauth'] = (data['oauth_token'], data['oauth_token_secret'])
			return HTTPSeeOther(twitter.get_authorize_url(data['oauth_token'], **params))
		else:
			request_token, request_token_secret = req_session.pop('twitter_oauth')
			creds = {
				'request_token': request_token,
				'request_token_secret': request_token_secret
				}
			params = {'oauth_verifier': auth_verifier}
			sess = twitter.get_auth_session(params=params, **creds)
			res_json = sess.get('account/verify_credentials.json',
							  params={'format':'json'}).json()
			print(res_json)
			#twitter does not provide email with rest api, we hawe to ask the user explicitly
			reg_params['username'] = res_json['screen_name'].replace(' ','').lower()
			reg_params['givenname'] = res_json['name'].split()[0]
			reg_params['familyname'] = res_json['name'].split()[-1]
			passwordhash = hashlib.sha224((auth_provider + reg_params['email'] + reg_params['username'] + str(res_json['id'])).encode('utf8')).hexdigest()
			reg_params['password'] = passwordhash[::3][:8]

			headers = client_oauth_register(request, reg_params)
			
			if headers:
				return HTTPSeeOther(location=request.route_url('access.cl.home'), headers=headers)

	return HTTPSeeOther(location=request.route_url('access.cl.login'))

@view_config(route_name='access.cl.oauthgoogle', request_method='GET')
def client_oauth_google(request):
	cfg = request.registry.settings
	loc = get_localizer(request)
	min_pwd_len = int(cfg.get('netprofile.client.registration.min_password_length', 8))
	auth_provider = 'google'
	reg_params = {
		'email':None,
		'username':None,
		'password':None,
		'givenname':None,
		'familyname':None,
		}

	GOOGLE_APP_ID = cfg.get('netprofile.client.GOOGLE_APP_ID', False)
	GOOGLE_APP_SECRET = cfg.get('netprofile.client.GOOGLE_APP_SECRET', False)

	gauthcode = request.GET.get('code', False)
	redirect_uri = request.route_url('access.cl.oauthgoogle')

	google = OAuth2Service(
		client_id=GOOGLE_APP_ID,
		client_secret=GOOGLE_APP_SECRET,
		name='google',
		authorize_url='https://accounts.google.com/o/oauth2/auth',
		access_token_url='https://accounts.google.com/o/oauth2/token',
		base_url='https://accounts.google.com/o/oauth2/auth',
		)

	if gauthcode is not False:
		gsession = google.get_auth_session(
			data={
				'code'         : gauthcode,
				'redirect_uri' : redirect_uri,
				'grant_type'   : 'authorization_code'
				},
			decoder=lambda b: json.loads(b.decode())
			)
		json_path = 'https://www.googleapis.com/oauth2/v1/userinfo'
		res_json = gsession.get(json_path).json()
		
		reg_params['email'] = res_json['email']
		reg_params['username'] = res_json['email'].split("@")[0]
		reg_params['givenname'] = res_json['given_name']
		reg_params['familyname'] = res_json['family_name']
		passwordhash = hashlib.sha224((auth_provider + reg_params['email'] + reg_params['username'] + res_json['id']).encode('utf8')).hexdigest()
		reg_params['password'] = passwordhash[::3][:8]
		
		headers = client_oauth_register(request, reg_params)
		if headers:
			return HTTPSeeOther(location=request.route_url('access.cl.home'), headers=headers)
		else:
			return HTTPSeeOther(location=request.route_url('access.cl.home'))

	if GOOGLE_APP_ID and GOOGLE_APP_SECRET:
		params = {
			'scope': 'email profile',
			'response_type': 'code',
			'redirect_uri': redirect_uri
			}
		authorize_url = google.get_authorize_url(**params)
		return HTTPSeeOther(authorize_url)

@view_config(route_name='access.cl.oauthfacebook', request_method='GET')
def client_oauth_facebook(request):
	if authenticated_userid(request):
		return HTTPSeeOther(location=request.route_url('access.cl.home'))

	cfg = request.registry.settings
	loc = get_localizer(request)
	min_pwd_len = int(cfg.get('netprofile.client.registration.min_password_length', 8))
	auth_provider = 'facebook'
	reg_params = {
		'email':None,
		'username':None,
		'password':None,
		'givenname':None,
		'familyname':None,
		}

	FACEBOOK_APP_ID = cfg.get('netprofile.client.FACEBOOK_APP_ID', False)
	FACEBOOK_APP_SECRET = cfg.get('netprofile.client.FACEBOOK_APP_SECRET', False)

	facebook = OAuth2Service(
		client_id=FACEBOOK_APP_ID,
		client_secret=FACEBOOK_APP_SECRET,
		name='facebook',
		authorize_url='https://graph.facebook.com/oauth/authorize',
		access_token_url='https://graph.facebook.com/oauth/access_token',
		base_url='https://graph.facebook.com/')

	fbauthcode = request.GET.get('code', False)

	redirect_uri = request.route_url('access.cl.oauthfacebook')
	if fbauthcode is not False:
		fbsession = facebook.get_auth_session(data={'code': fbauthcode,	'redirect_uri': redirect_uri})
		res_json = fbsession.get('me').json()
		reg_params['email'] = res_json['email']
		reg_params['username'] = res_json['name'].replace(' ','').lower()
		reg_params['givenname'] = res_json['first_name']
		reg_params['familyname'] = res_json['last_name']
		passwordhash = hashlib.sha224((auth_provider + reg_params['email'] + reg_params['username'] + res_json['id']).encode('utf8')).hexdigest()
		reg_params['password'] = passwordhash[::3][:8]

		headers = client_oauth_register(request, reg_params)

		if headers:
			return HTTPSeeOther(location=request.route_url('access.cl.home'), headers=headers)

	if FACEBOOK_APP_ID and FACEBOOK_APP_SECRET:
		params = {'scope': 'email',
				  'response_type': 'code',
				  'redirect_uri': redirect_uri}
		authorize_url = facebook.get_authorize_url(**params)
		return HTTPSeeOther(authorize_url)
		
@view_config(route_name='access.cl.oauthreg')
def client_oauth_register(request, regdict):
	nxt = request.route_url('access.cl.home')
	loc = get_localizer(request)
	headers = None
	#if authenticated_userid(request):
	#	 return HTTPSeeOther(location=nxt)

	cfg = request.registry.settings
	rate_id = int(cfg.get('netprofile.client.registration.rate_id', 1))
	state_id = int(cfg.get('netprofile.client.registration.state_id', 1))

	errors = {}
	sess = DBSession()

	login = regdict.get('username', None)
	passwd = regdict.get('password', None)
	email = regdict.get('email', None)
	name_family = regdict.get('familyname', '')
	name_given = regdict.get('givenname', '')

	### !!!!! What if user changes his password in out database?!
	if login is not None and passwd is not None:
		q = sess.query(AccessEntity).filter(AccessEntity.nick == login, AccessEntity.access_state != AccessState.block_inactive.value)
		if q is not None:
			for user in q:
				if user.password == passwd:
					headers = remember(request, login)
					return headers

	if headers is None:
		ent = PhysicalEntity()
		ent.nick = login
		ent.email = email
		ent.name_family = name_family
		ent.name_given = name_given
		ent.state_id = state_id

		stash = Stash()
		stash.entity = ent
		stash.name = loc.translate(_('Primary Account'))

		acc = AccessEntity()
		acc.nick = login
		acc.password = passwd
		acc.stash = stash
		acc.rate_id = rate_id
		acc.state_id = state_id
		ent.children.append(acc)
		
		sess.add(ent)
		sess.add(stash)
		sess.add(acc)
		sess.flush()
		headers = remember(request, login)
		return headers

	else:
		return False

@view_config(route_name='access.cl.register', renderer='netprofile_access:templates/client_register.mak')
def client_register(request):
	if authenticated_userid(request):
		return HTTPSeeOther(location=request.route_url('access.cl.home'))
	cur_locale = locale_neg(request)
	loc = get_localizer(request)
	cfg = request.registry.settings
	comb_js = asbool(cfg.get('netprofile.client.combine_js', False))
	can_reg = asbool(cfg.get('netprofile.client.registration.enabled', False))
	must_verify = asbool(cfg.get('netprofile.client.registration.verify_email', True))
	must_recaptcha = asbool(cfg.get('netprofile.client.registration.recaptcha.enabled', False))
	min_pwd_len = int(cfg.get('netprofile.client.registration.min_password_length', 8))
	rate_id = int(cfg.get('netprofile.client.registration.rate_id', 1))
	state_id = int(cfg.get('netprofile.client.registration.state_id', 1))
	maillogin = asbool(cfg.get('netprofile.client.email_as_username', False))
	csrf = request.POST.get('csrf', '')
	errors = {}
	if not can_reg:
		return HTTPSeeOther(location=request.route_url('access.cl.login'))
	if must_recaptcha:
		rc_private = cfg.get('netprofile.client.recaptcha.private_key')
		rc_public = cfg.get('netprofile.client.recaptcha.public_key')
		if (not rc_private) or (not rc_public):
			# TODO: log missing reCAPTCHA keys
			must_recaptcha = False
	if 'submit' in request.POST:
		sess = DBSession()
		if csrf != request.get_csrf():
			errors['csrf'] = _('Error submitting form')
		elif must_recaptcha:
			try:
				rcresp = verify_recaptcha(rc_private, request)
			except ValueError as e:
				errors['recaptcha'] = str(e)
			else:
				if rcresp and not rcresp.valid:
					errors['recaptcha'] = rcresp.text()
		if len(errors) == 0:
			login = request.POST.get('user', '')
			passwd = request.POST.get('pass', '')
			passwd2 = request.POST.get('pass2', '')
			email = request.POST.get('email', '')
			name_family = request.POST.get('name_family', '')
			name_given = request.POST.get('name_given', '')
			name_middle = request.POST.get('name_middle', '')
			l = len(login)
			if (l == 0) or (l > 254):
				errors['user'] = _('Invalid field length')
			elif not maillogin and not _re_login.match(login):
				errors['user'] = _('Invalid character used in username')
			l = len(passwd)
			if l < min_pwd_len:
				errors['pass'] = _('Password is too short')
			elif l > 254:
				errors['pass'] = _('Password is too long')
			if passwd != passwd2:
				errors['pass2'] = _('Passwords do not match')
			l = len(email)
			if (l == 0) or (l > 254):
				errors['email'] = _('Invalid field length')
			elif not _re_email.match(email):
				errors['email'] = _('Invalid e-mail format')
			if maillogin:
				login = email
			l = len(name_family)
			if (l == 0) or (l > 254):
				errors['name_family'] = _('Invalid field length')
			l = len(name_given)
			if (l == 0) or (l > 254):
				errors['name_given'] = _('Invalid field length')
			l = len(name_middle)
			if l > 254:
				errors['name_middle'] = _('Invalid field length')
			if 'user' not in errors:
				# XXX: currently we check across all entity types.
				login_clash = sess.query(func.count('*'))\
					.select_from(Entity)\
					.filter(Entity.nick == login)\
					.scalar()
				if login_clash > 0:
					errors['user'] = _('This username is already taken')
		if len(errors) == 0:
			ent = PhysicalEntity()
			ent.nick = login
			ent.email = email
			ent.name_family = name_family
			ent.name_given = name_given
			if name_middle:
				ent.name_middle = name_middle
			ent.state_id = state_id

			stash = Stash()
			stash.entity = ent
			stash.name = loc.translate(_('Primary Account'))

			acc = AccessEntity()
			acc.nick = login
			acc.password = passwd
			acc.stash = stash
			acc.rate_id = rate_id
			acc.state_id = state_id
			ent.children.append(acc)

			sess.add(ent)
			sess.add(stash)
			sess.add(acc)

			if must_verify:
				link_id = int(cfg.get('netprofile.client.registration.link_id', 1))
				rand_len = int(cfg.get('netprofile.client.registration.code_length', 20))
				queue_mail = asbool(cfg.get('netprofile.client.registration.mail_queue', False))
				sender = cfg.get('netprofile.client.registration.mail_sender')

				acc.access_state = AccessState.block_inactive.value
				link = AccessEntityLink()
				link.entity = acc
				link.type_id = link_id

				chars = string.ascii_uppercase + string.digits
				try:
					rng = random.SystemRandom()
				except NotImplementedError:
					rng = random
				link.value = ''.join(rng.choice(chars) for i in range(rand_len))
				link.timestamp = datetime.datetime.now()
				sess.add(link)

				mailer = get_mailer(request)

				tpldef = {
					'cur_loc' : cur_locale,
					'entity'  : ent,
					'stash'   : stash,
					'access'  : acc,
					'link'    : link
				}
				request.run_hook('access.cl.tpldef.register.mail', tpldef, request)
				msg_text = Attachment(
					data=render('netprofile_access:templates/email_register_plain.mak', tpldef, request),
					content_type='text/plain; charset=\'utf-8\'',
					disposition='inline',
					transfer_encoding='quoted-printable'
				)
				msg_html = Attachment(
					data=render('netprofile_access:templates/email_register_html.mak', tpldef, request),
					content_type='text/html; charset=\'utf-8\'',
					disposition='inline',
					transfer_encoding='quoted-printable'
				)
				msg = Message(
					subject=(loc.translate(_('Activation required for user %s')) % login),
					sender=sender,
					recipients=(email,),
					body=msg_text,
					html=msg_html
				)
				if queue_mail:
					mailer.send_to_queue(msg)
				else:
					mailer.send(msg)
			return HTTPSeeOther(location=request.route_url('access.cl.regsent'))
	tpldef = {
		'cur_loc'        : cur_locale,
		'comb_js'        : comb_js,
		'must_verify'    : must_verify,
		'must_recaptcha' : must_recaptcha,
		'min_pwd_len'    : min_pwd_len,
		'maillogin'      : maillogin,
		'errors'         : {err: loc.translate(errors[err]) for err in errors}
	}
	if must_recaptcha:
		tpldef['rc_public'] = rc_public
	request.run_hook('access.cl.tpldef.register', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.check.nick', xhr=True, renderer='json')
def client_check_nick(request):
	login = request.GET.get('value')
	ret = {'value' : login, 'valid' : False}
	if 'X-CSRFToken' not in request.headers:
		return ret
	if request.headers['X-CSRFToken'] != request.get_csrf():
		return ret
	if authenticated_userid(request):
		return ret
	cfg = request.registry.settings
	can_reg = asbool(cfg.get('netprofile.client.registration.enabled', False))
	if not can_reg:
		return ret
	sess = DBSession()
	# XXX: currently we check across all entity types.
	login_clash = sess.query(func.count('*'))\
		.select_from(Entity)\
		.filter(Entity.nick == str(login))\
		.scalar()
	if login_clash == 0:
		loc = get_localizer(request)
		ret['valid'] = True
	return ret

@view_config(route_name='access.cl.regsent', renderer='netprofile_access:templates/client_regsent.mak')
def client_regsent(request):
	if authenticated_userid(request):
		return HTTPSeeOther(location=request.route_url('access.cl.home'))
	cur_locale = locale_neg(request)
	cfg = request.registry.settings
	comb_js = asbool(cfg.get('netprofile.client.combine_js', False))
	can_reg = asbool(cfg.get('netprofile.client.registration.enabled', False))
	must_verify = asbool(cfg.get('netprofile.client.registration.verify_email', True))
	if not can_reg:
		return HTTPSeeOther(location=request.route_url('access.cl.login'))
	tpldef = {
		'cur_loc'        : cur_locale,
		'comb_js'        : comb_js,
		'must_verify'    : must_verify
	}
	request.run_hook('access.cl.tpldef.regsent', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.activate', renderer='netprofile_access:templates/client_activate.mak')
def client_activate(request):
	if authenticated_userid(request):
		return HTTPSeeOther(location=request.route_url('access.cl.home'))
	did_fail = True
	cur_locale = locale_neg(request)
	cfg = request.registry.settings
	comb_js = asbool(cfg.get('netprofile.client.combine_js', False))
	can_reg = asbool(cfg.get('netprofile.client.registration.enabled', False))
	must_verify = asbool(cfg.get('netprofile.client.registration.verify_email', True))
	link_id = int(cfg.get('netprofile.client.registration.link_id', 1))
	rand_len = int(cfg.get('netprofile.client.registration.code_length', 20))
	if (not can_reg) or (not must_verify):
		return HTTPSeeOther(location=request.route_url('access.cl.login'))
	code = request.GET.get('code', '').strip().upper()
	login = request.GET.get('for', '')
	if code and login and (len(code) == rand_len):
		sess = DBSession()
		for link in sess.query(AccessEntityLink)\
				.options(joinedload(AccessEntityLink.entity))\
				.filter(AccessEntityLink.type_id == link_id, AccessEntityLink.value == code):
			# TODO: implement code timeouts
			ent = link.entity
			if (ent.access_state == AccessState.block_inactive.value) and (ent.nick == login):
				ent.access_state = AccessState.ok.value
				sess.delete(link)
				did_fail = False
				break
	tpldef = {
		'failed'         : did_fail,
		'comb_js'        : comb_js,
		'cur_loc'        : cur_locale
	}
	request.run_hook('access.cl.tpldef.activate', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.restorepass', renderer='netprofile_access:templates/client_restorepass.mak')
def client_restorepass(request):
	if authenticated_userid(request):
		return HTTPSeeOther(location=request.route_url('access.cl.home'))
	did_fail = True
	cur_locale = locale_neg(request)
	loc = get_localizer(request)
	cfg = request.registry.settings
	comb_js = asbool(cfg.get('netprofile.client.combine_js', False))
	can_rp = asbool(cfg.get('netprofile.client.password_recovery.enabled', False))
	change_pass = asbool(cfg.get('netprofile.client.password_recovery.change_password', True))
	must_recaptcha = asbool(cfg.get('netprofile.client.password_recovery.recaptcha.enabled', False))
	maillogin = asbool(cfg.get('netprofile.client.email_as_username', False))
	errors = {}
	if not can_rp:
		return HTTPSeeOther(location=request.route_url('access.cl.login'))
	if must_recaptcha:
		rc_private = cfg.get('netprofile.client.recaptcha.private_key')
		rc_public = cfg.get('netprofile.client.recaptcha.public_key')
		if (not rc_private) or (not rc_public):
			# TODO: log missing reCAPTCHA keys
			must_recaptcha = False
	if 'submit' in request.POST:
		csrf = request.POST.get('csrf', '')
		if csrf != request.get_csrf():
			errors['csrf'] = _('Error submitting form')
		elif must_recaptcha:
			try:
				rcresp = verify_recaptcha(rc_private, request)
			except ValueError as e:
				errors['recaptcha'] = str(e)
			else:
				if rcresp and not rcresp.valid:
					errors['recaptcha'] = rcresp.text()
		if len(errors) == 0:
			login = request.POST.get('user', '')
			email = request.POST.get('email', '')
			if maillogin:
				login = email
			l = len(login)
			if (l == 0) or (l > 254):
				errors['user'] = _('Invalid field length')
			elif not _re_login.match(login):
				errors['user'] = _('Invalid character used in username')
			l = len(email)
			if (l == 0) or (l > 254):
				errors['email'] = _('Invalid field length')
			elif not _re_email.match(email):
				errors['email'] = _('Invalid e-mail format')
		if len(errors) == 0:
			sess = DBSession()
			for acc in sess.query(AccessEntity)\
					.filter(AccessEntity.nick == login, AccessEntity.access_state != AccessState.block_inactive.value):
				ent = acc.parent
				ent_email = None
				while ent:
					if isinstance(ent, PhysicalEntity):
						ent_email = ent.email
					elif isinstance(ent, LegalEntity):
						ent_email = ent.contact_email
					if email == ent_email:
						break
					ent = ent.parent
				if email == ent_email:
					queue_mail = asbool(cfg.get('netprofile.client.password_recovery.mail_queue', False))
					sender = cfg.get('netprofile.client.password_recovery.mail_sender')

					if change_pass:
						pwd_len = int(cfg.get('netprofile.client.password_recovery.password_length', 12))
						chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
						try:
							rng = random.SystemRandom()
						except NotImplementedError:
							rng = random
						acc.password = ''.join(rng.choice(chars) for i in range(pwd_len))

					mailer = get_mailer(request)
					tpldef = {
						'cur_loc'     : cur_locale,
						'entity'      : ent,
						'email'       : ent_email,
						'access'      : acc,
						'change_pass' : change_pass
					}
					request.run_hook('access.cl.tpldef.password_recovery.mail', tpldef, request)
					msg_text = Attachment(
						data=render('netprofile_access:templates/email_recover_plain.mak', tpldef, request),
						content_type='text/plain; charset=\'utf-8\'',
						disposition='inline',
						transfer_encoding='quoted-printable'
					)
					msg_html = Attachment(
						data=render('netprofile_access:templates/email_recover_html.mak', tpldef, request),
						content_type='text/html; charset=\'utf-8\'',
						disposition='inline',
						transfer_encoding='quoted-printable'
					)
					msg = Message(
						subject=(loc.translate(_('Password recovery for user %s')) % login),
						sender=sender,
						recipients=(ent_email,),
						body=msg_text,
						html=msg_html
					)
					if queue_mail:
						mailer.send_to_queue(msg)
					else:
						mailer.send(msg)
					return HTTPSeeOther(location=request.route_url('access.cl.restoresent'))
			else:
				errors['csrf'] = _('Username and/or e-mail are unknown to us')
	tpldef = {
		'cur_loc'        : cur_locale,
		'comb_js'        : comb_js,
		'change_pass'    : change_pass,
		'must_recaptcha' : must_recaptcha,
		'maillogin'      : maillogin,
		'errors'         : {err: loc.translate(errors[err]) for err in errors}
	}
	if must_recaptcha:
		tpldef['rc_public'] = rc_public
	request.run_hook('access.cl.tpldef.restorepass', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.restoresent', renderer='netprofile_access:templates/client_restoresent.mak')
def client_restoresent(request):
	if authenticated_userid(request):
		return HTTPSeeOther(location=request.route_url('access.cl.home'))
	cur_locale = locale_neg(request)
	cfg = request.registry.settings
	comb_js = asbool(cfg.get('netprofile.client.combine_js', False))
	can_rp = asbool(cfg.get('netprofile.client.password_recovery.enabled', False))
	if not can_rp:
		return HTTPSeeOther(location=request.route_url('access.cl.login'))
	change_pass = asbool(cfg.get('netprofile.client.password_recovery.change_password', True))
	tpldef = {
		'cur_loc'     : cur_locale,
		'comb_js'     : comb_js,
		'change_pass' : change_pass
	}
	request.run_hook('access.cl.tpldef.restoresent', tpldef, request)
	return tpldef



@view_config(route_name='access.cl.logout')
def client_logout(request):
	headers = forget(request)
	request.session.invalidate()
	request.session.new_csrf_token()
	loc = request.route_url('access.cl.login')
	return HTTPSeeOther(location=loc, headers=headers)

@view_config(route_name='access.cl.robots')
def client_robots(request):
	return Response("""User-agent: *
Disallow: /
""".encode(), content_type='text/plain; charset=utf-8')

@view_config(route_name='access.cl.favicon')
def client_bogus_favicon(request):
	icon = os.path.join(
		os.path.dirname(__file__),
		'static',
		'favicon.ico'
	)
	return FileResponse(icon, request=request)

@register_hook('access.cl.tpldef')
def _cl_tpldef(tpldef, req):
	cfg = req.registry.settings
	comb_js = asbool(cfg.get('netprofile.client.combine_js', False))
	cur_locale = get_locale_name(req)
	loc = get_localizer(req)
	menu = [{
		'route' : 'access.cl.home',
		'text'  : _('Portal')
	}]
	if 'trans' in tpldef:
		tpldef['trans'] = {txt: loc.translate(txt) for txt in tpldef['trans']}
	req.run_hook('access.cl.menu', menu, req)
	tpldef.update({
		'menu'    : menu,
		'cur_loc' : cur_locale,
		'comb_js' : comb_js,
		'loc'     : loc,
		'i18n'    : Locale(cur_locale)
	})

@view_config(
	route_name='stashes.cl.accounts',
	name='chrate',
	context=Stash,
	request_method='POST',
	permission='USAGE'
)
def client_chrate(ctx, request):
	loc = get_localizer(request)
	csrf = request.POST.get('csrf', '')
	rate_id = int(request.POST.get('rateid'), 0)
	aent_id = int(request.POST.get('entityid'))
	ent = request.user.parent
	err = True

	if csrf == request.get_csrf():
		sess = DBSession()
		aent = sess.query(AccessEntity).get(aent_id)
		if ent and aent and (aent.parent == ent) and (aent in ctx.access_entities):
			err = False
			if 'clear' in request.POST:
				rate_id = None
				aent.next_rate_id = None
			elif rate_id > 0:
				aent.next_rate_id = rate_id

	if err:
		request.session.flash({
			'text' : loc.translate(_('Error scheduling rate change')),
			'class' : 'danger'
		})
	elif rate_id:
		request.session.flash({
			'text' : loc.translate(_('Rate change successfully scheduled'))
		})
	else:
		request.session.flash({
			'text' : loc.translate(_('Rate change successfully cancelled'))
		})
	return HTTPSeeOther(location=request.route_url('stashes.cl.accounts', traverse=()))

@register_hook('access.cl.tpldef.accounts.list')
def _tpldef_list_accounts(tpldef, req):
	sess = DBSession()
	# FIXME: add classes etc.
	tpldef['rates'] = sess.query(Rate).filter(Rate.user_selectable == True)

@register_hook('core.dpanetabs.access.AccessEntity')
def _dpane_aent_mods(tabs, model, req):
	loc = get_localizer(req)
	tabs.extend(({
		'title'             : loc.translate(_('Rate Modifiers')),
		'iconCls'           : 'ico-mod-ratemodifiertype',
		'xtype'             : 'grid_access_PerUserRateModifier',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Access Blocks')),
		'iconCls'           : 'ico-mod-accessblock',
		'xtype'             : 'grid_access_AccessBlock',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Links')),
		'iconCls'           : 'ico-mod-accessentitylink',
		'xtype'             : 'grid_access_AccessEntityLink',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}))

