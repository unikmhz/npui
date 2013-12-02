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

from pyramid.view import (
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
from netprofile import (
	LANGUAGES,
	locale_neg
)
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from .models import AccessEntity

_ = TranslationStringFactory('netprofile_access')

@view_config(route_name='access.cl.home', renderer='netprofile_access:templates/client_home.mak', permission='USAGE')
def client_home(request):
	tpldef = {}
	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.home', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.login', renderer='netprofile_access:templates/client_login.mak')
def client_login(request):
	nxt = request.route_url('access.cl.home')
	if authenticated_userid(request):
		return HTTPFound(location=nxt)
	login = ''
	did_fail = False
	cur_locale = locale_neg(request)

	if 'submit' in request.POST:
		login = request.POST.get('user', '')
		passwd = request.POST.get('pass', '')
		csrf = request.POST.get('csrf', '')

		if (csrf == request.get_csrf()) and login:
			sess = DBSession()
			q = sess.query(AccessEntity).filter(AccessEntity.nick == login)
			for user in q:
				if user.password == passwd:
					headers = remember(request, login)
					return HTTPFound(location=nxt, headers=headers)
		did_fail = True

	tpldef = {
		'login'   : login,
		'failed'  : did_fail,
		'langs'   : LANGUAGES,
		'cur_loc' : cur_locale
	}
	request.run_hook('access.cl.tpldef.login', tpldef, request)
	return tpldef

@view_config(route_name='access.cl.logout')
def client_logout(request):
	headers = forget(request)
	request.session.invalidate()
	request.session.new_csrf_token()
	loc = request.route_url('access.cl.login')
	return HTTPFound(location=loc, headers=headers)

@register_hook('access.cl.tpldef')
def _cl_tpldef(tpldef, req):
	cur_locale = get_locale_name(req)
	loc = get_localizer(req)
	menu = [{
		'route' : 'access.cl.home',
		'text'  : _('Portal')
	}]
	req.run_hook('access.cl.menu', menu, req)
	menu.extend(({
		'route' : 'access.cl.logout',
		'text'  : _('Log Out'),
		'cls'   : 'bottom'
	},))
	tpldef.update({
		'menu'    : menu,
		'cur_loc' : cur_locale,
		'loc'     : loc
	})

