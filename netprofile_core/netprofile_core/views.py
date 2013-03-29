#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.response import Response
from pyramid.i18n import get_locale_name
from pyramid.view import (
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
	HTTPNotFound
)

from sqlalchemy import and_
from sqlalchemy.exc import DBAPIError

from netprofile import (
	LANGUAGES,
	locale_neg
)
from netprofile.common.modules import IModuleManager
from netprofile.db.connection import DBSession
from netprofile.ext.direct import extdirect_method

from .models import (
	NPModule,
	User,
	UserSetting,
	UserSettingSection,
	UserSettingType,
	UserState
)

@view_config(route_name='core.home', renderer='netprofile_core:templates/home.mak', permission='USAGE')
def home_screen(request):
	mmgr = request.registry.getUtility(IModuleManager)
	lang = get_locale_name(request)
	tpldef = {
		'res_css' : mmgr.get_css(request),
		'res_js'  : mmgr.get_js(request),
		'res_ljs' : mmgr.get_local_js(request, lang),
		'cur_loc' : lang
	}
	return tpldef

@forbidden_view_config()
def do_forbidden(request):
	if authenticated_userid(request):
		return HTTPForbidden()
	loc = request.route_url('core.login', _query=(('next', request.path),))
	return HTTPFound(location=loc)

@view_config(route_name='core.login', renderer='netprofile_core:templates/login.mak')
def do_login(request):
	nxt = request.params.get('next')
	if (not nxt) or (not nxt.startswith('/')):
		nxt = request.route_url('core.home')
	if authenticated_userid(request):
		return HTTPFound(location=nxt)
	login = ''
	did_fail = False
	cur_locale = locale_neg(request)
	if 'submit' in request.POST:
		login = request.POST.get('user', '')
		passwd = request.POST.get('pass', '')
		csrf = request.POST.get('csrf', '')

		if csrf == request.get_csrf():
			sess = DBSession()
			reg = request.registry
			hash_con = reg.settings.get('netprofile.auth.hash', 'sha1')
			salt_len = int(reg.settings.get('netprofile.auth.salt_length', 4))
			q = sess.query(User).filter(User.state == UserState.active).filter(User.enabled == True).filter(User.login == login)
			for user in q:
				if user.check_password(passwd, hash_con, salt_len):
					headers = remember(request, login)
					if 'auth.acls' in request.session:
						del request.session['auth.acls']
					if 'auth.settings' in request.session:
						del request.session['auth.settings']
					return HTTPFound(location=nxt, headers=headers)
		did_fail = True

	mmgr = request.registry.getUtility(IModuleManager)

	return {
		'login'   : login,
		'next'    : nxt,
		'failed'  : did_fail,
		'res_css' : mmgr.get_css(request),
		'res_js'  : mmgr.get_js(request),
		'res_ljs' : mmgr.get_local_js(request, cur_locale),
		'langs'   : LANGUAGES,
		'cur_loc' : cur_locale
	}

@view_config(route_name='core.noop', permission='USAGE')
def do_noop(request):
	if request.referer:
		return HTTPFound(location=request.referer)
	return HTTPFound(location=request.route_url('core.home'))

@view_config(route_name='core.logout')
def do_logout(request):
	if 'auth.acls' in request.session:
		del request.session['auth.acls']
	if 'auth.settings' in request.session:
		del request.session['auth.settings']
	headers = forget(request)
	request.session.invalidate()
	request.session.new_csrf_token()
	loc = request.route_url('core.login')
	return HTTPFound(location=loc, headers=headers)

@view_config(route_name='core.js.webshell', renderer='netprofile_core:templates/webshell.mak', permission='USAGE')
def js_webshell(request):
	mmgr = request.registry.getUtility(IModuleManager)
	return {
		'langs'   : LANGUAGES,
		'cur_loc' : get_locale_name(request),
		'res_ajs' : mmgr.get_autoload_js(request),
		'modules' : mmgr.get_module_browser()
	}

def dpane_simple(model, request):
	tabs = []
	request.run_hook(
		'core.dpanetabs.%s.%s' % (model.__parent__.moddef, model.name),
		tabs, model, request
	)
	cont = {
		'border' : 0,
		'layout' : {
			'type'    : 'hbox',
			'align'   : 'stretch',
			'padding' : 4
		},
		'items' : [{
			'xtype' : 'npform',
			'flex'  : 2
		}, {
			'xtype' : 'splitter'
		}, {
			'xtype'  : 'tabpanel',
			'flex'   : 3,
			'items'  : tabs
		}]
	}
	request.run_hook(
		'core.dpane.%s.%s' % (model.__parent__.moddef, model.name),
		cont, model, request
	)
	return cont

@extdirect_method('DataCache', 'save_ls', request_as_last_param=True, permission='USAGE')
def localstorage_save(params, request):
	"""
	ExtDirect method to save local storage state.
	"""

	assert isinstance(params, dict), 'Dictionary required'

	user = request.user
	if user:
		user.data_cache['ls'] = params
		return { 'success' : True }
	return {
		'success' : False,
		'message' : 'No such user or anonymous'
	}

@extdirect_method('DataCache', 'load_ls', request_as_last_param=True, permission='USAGE')
def localstorage_load(request):
	"""
	ExtDirect method to restore local storage state.
	"""

	user = request.user
	if user:
		return {
			'success' : True,
			'state'   : user.data_cache.get('ls', {})
		}
	return {
		'success' : False,
		'message' : 'No such user or anonymous'
	}

@extdirect_method('MenuTree', 'settings', request_as_last_param=True, permission='USAGE')
def menu_settings(params, request):
	"""
	ExtDirect method for settings menu tree.
	"""

	menu = []
	mmgr = request.registry.getUtility(IModuleManager)
	sess = DBSession()

	if params['node'] == 'root':
		for mod in sess \
					.query(NPModule) \
					.filter(NPModule.name.in_(mmgr.loaded.keys())) \
					.filter(NPModule.enabled == True):
			mod_name = mod.name
			if isinstance(mod_name, bytes):
				mod_name = mod_name.decode()
			mi = mod.get_tree_node(request, mmgr.loaded[mod.name])
			mi['expanded'] = False
			menu.append(mi)
		return {
			'success' : True,
			'records' : menu,
			'total'   : len(menu)
		}

	if params['node'] not in mmgr.loaded:
		raise ValueError('Unknown module name requested: %s' % params['node'])

	mod = sess.query(NPModule).filter(NPModule.name == params['node']).one()
	for uss in sess.query(UserSettingSection).filter(UserSettingSection.module == mod):
		mi = uss.get_tree_node(request)
		mi['xhandler'] = 'NetProfile.controller.UserSettingsForm'
		menu.append(mi)

	return {
		'success' : True,
		'records' : menu
	}

@extdirect_method('UserSetting', 'usform_get', request_as_last_param=True, permission='USAGE')
def dyn_usersettings_form(param, request):
	"""
	ExtDirect method to populate setting section form.
	"""

	sid = int(param['section'])
	form = []
	sess = DBSession()
	sect = sess.query(UserSettingSection).get(sid)
	for (ust, us) in sess \
			.query(UserSettingType, UserSetting) \
			.outerjoin(UserSetting, and_(
				UserSettingType.id == UserSetting.type_id,
				UserSetting.user_id == request.user.id
			)) \
			.filter(UserSettingType.section_id == sid):
		field = ust.get_field_cfg(request)
		if field:
			if us and (us.value is not None):
				field['value'] = ust.parse_param(us.value)
				if (ust.type == 'checkbox') and field['value']:
					field['checked'] = True
				else:
					field['checked'] = False
			elif ust.default is not None:
				field['value'] = ust.parse_param(ust.default)
			else:
				field['value'] = None
			form.append(field)
	return {
		'success' : True,
		'fields'  : form,
		'section' : {
			'id'    : sect.id,
			'name'  : sect.name,
			'descr' : sect.description
		}
	}

@extdirect_method('UserSetting', 'usform_submit', request_as_last_param=True, permission='USAGE', accepts_files=True)
def dyn_usersettings_submit(param, request):
	"""
	ExtDirect method for submitting user setting section form.
	"""

	sess = DBSession()
	s = None
	if 'auth.settings' in request.session:
		s = request.session['auth.settings']
	for (ust, us) in sess \
		.query(UserSettingType, UserSetting) \
		.outerjoin(UserSetting, and_(
			UserSettingType.id == UserSetting.type_id,
			UserSetting.user_id == request.user.id
		)) \
		.filter(UserSettingType.name.in_(param.keys())):
			if ust.name in param:
				if us:
					us.value = ust.param_to_db(param[ust.name])
				else:
					us = UserSetting()
					us.user = request.user
					us.type = ust
					us.value = ust.param_to_db(param[ust.name])
					sess.add(us)
				if s:
					s[ust.name] = ust.parse_param(param[ust.name])
	if s:
		request.session['auth.settings'] = s
	return {
		'success' : True
	}

@extdirect_method('UserSetting', 'client_get', request_as_last_param=True, permission='USAGE')
def dyn_usersettings_client(request):
	"""
	ExtDirect method for updating client-side user settings.
	"""

	return {
		'success'  : True,
		'settings' : request.user.client_settings(request)
	}

