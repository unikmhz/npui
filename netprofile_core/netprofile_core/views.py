#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Core module - Views
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

import json
import logging
import datetime as dt
from collections import (
	defaultdict,
	Iterable
)
from dateutil.parser import parse as dparse

from pyramid.response import Response
from pyramid.security import has_permission
from pyramid.i18n import get_locale_name
from pyramid.view import (
	forbidden_view_config,
	notfound_view_config,
	view_config
)
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import (
	HTTPForbidden,
	HTTPFound,
	HTTPNotFound,
	HTTPSeeOther
)

from sqlalchemy import (
	and_,
	or_,
	func
)
from sqlalchemy.orm import undefer

from netprofile import locale_neg
from netprofile import PY3
from netprofile.common.auth import (
	auth_add,
	auth_remove
)
from netprofile.common.util import make_config_dict
from netprofile.common.modules import IModuleManager
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession
from netprofile.ext.data import ExtModel
from netprofile.ext.direct import extdirect_method
from netprofile.ext.wizards import (
	ExtJSWizardField,
	Step,
	Wizard
)
from netprofile.dav import DAVMountResponse

from .models import (
	Calendar,
	CalendarAccess,
	CalendarImport,
	Event,
	File,
	FileFolder,
	Group,
	GroupCapability,
	NPModule,
	Privilege,
	User,
	UserCapability,
	UserSetting,
	UserSettingSection,
	UserSettingType,
	UserState,

	F_DEFAULT_FILES,
	secpol_errors
)

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_core')

if PY3:
	from html import escape as html_escape
else:
	from cgi import escape as html_escape

logger = logging.getLogger(__name__)

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

@notfound_view_config(vhost='MAIN', renderer='netprofile_core:templates/404.mak')
def do_notfound(request):
	mmgr = request.registry.getUtility(IModuleManager)
	lang = get_locale_name(request)
	request.response.status_code = 404
	return {
		'res_css' : mmgr.get_css(request),
		'res_js'  : mmgr.get_js(request),
		'res_ljs' : mmgr.get_local_js(request, lang),
		'cur_loc' : lang
	}

@forbidden_view_config(vhost='MAIN', renderer='netprofile_core:templates/403.mak')
def do_forbidden(request):
	mmgr = request.registry.getUtility(IModuleManager)
	lang = get_locale_name(request)
	request.response.status_code = 403
	return {
		'res_css' : mmgr.get_css(request),
		'res_js'  : mmgr.get_js(request),
		'res_ljs' : mmgr.get_local_js(request, lang),
		'cur_loc' : lang
	}

@view_config(route_name='core.login', renderer='netprofile_core:templates/login.mak')
def do_login(request):
	if authenticated_userid(request):
		return HTTPFound(location=request.route_url('core.home'))
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
					return auth_add(request, login, 'core.home')
		did_fail = True

	mmgr = request.registry.getUtility(IModuleManager)

	return {
		'login'   : login,
		'failed'  : did_fail,
		'res_css' : mmgr.get_css(request),
		'res_js'  : mmgr.get_js(request),
		'res_ljs' : mmgr.get_local_js(request, cur_locale),
		'cur_loc' : cur_locale
	}

@view_config(route_name='core.noop', permission='USAGE')
def do_noop(request):
	# Force locale renegotiation if necessary
	request.locale_name
	return HTTPFound(location=request.route_url('core.home'))

@view_config(route_name='core.logout')
def do_logout(request):
	return auth_remove(request, 'core.login')

@view_config(route_name='core.js.webshell', renderer='netprofile_core:templates/webshell.mak', permission='USAGE')
def js_webshell(request):
	request.response.content_type = 'text/javascript'
	request.response.charset = 'UTF-8'
	rtcfg = make_config_dict(request.registry.settings, 'netprofile.rt.')
	mmgr = request.registry.getUtility(IModuleManager)
	return {
		'cur_loc' : get_locale_name(request),
		'res_ajs' : mmgr.get_autoload_js(request),
		'res_ctl' : mmgr.get_controllers(request),
		'rt_host' : rtcfg.get('host', 'localhost'),
		'rt_port' : rtcfg.get('port', 8808),
		'pw_age'  : request.session.get('sess.pwage', 'ok'),
		'pw_days' : request.session.get('sess.pwdays', 0),
		'modules' : mmgr.get_module_browser()
	}

# No authentication!
@view_config(route_name='core.wellknown')
def wellknown_redirect(request):
	svc = request.matchdict.get('service')
	if svc and len(svc):
		svc = str(svc[0]).lower().strip(' /')
	else:
		return HTTPNotFound()
	if svc in ('dav', 'webdav', 'caldav', 'carddav'):
		return HTTPFound(location=request.route_url('core.dav', traverse=()))
	return HTTPNotFound()

# No authentication!
@view_config(route_name='core.logout.direct', renderer='json')
def do_logout_extdirect(request):
	return {
		'type' : 'event',
		'name' : 'sesstimeout'
	}

@view_config(route_name='core.file.download', permission='FILES_LIST')
def file_dl(request):
	try:
		file_id = int(request.matchdict.get('fileid', 0))
	except (TypeError, ValueError):
		raise KeyError('Invalid file ID')
	if file_id <= 0:
		raise KeyError('Invalid file ID')
	sess = DBSession()
	obj = sess.query(File)
	if request.method != 'HEAD':
		obj = obj.options(undefer('data'))
	obj = obj.get(file_id)
	res = obj.get_response(request)
	return res

@view_config(route_name='core.file.upload', permission='FILES_UPLOAD')
def file_ul(request):
	sess = DBSession()
	try:
		ff_id = request.POST['ffid']
	except KeyError:
		ff_id = None
	folder = None
	if ff_id:
		ff_id = int(ff_id)
		folder = sess.query(FileFolder).get(ff_id)
	if folder and not folder.can_write(request.user):
		raise ValueError('Folder access denied')
	for fo in request.POST.getall('file'):
		obj = File(
			user_id=request.user.id,
			user=request.user,
			group_id=request.user.group.id,
			group=request.user.group,
			rights=F_DEFAULT_FILES
		)
		if fo.filename:
			obj.name = obj.filename = fo.filename
		obj.folder = folder
		sess.add(obj)
		obj.set_from_file(fo.file, request.user, sess)
	res = Response(html_escape(json.dumps({
		'success' : True,
		'msg'     : 'File(s) uploaded'
	}), False))
	res.headerlist.append(('X-Frame-Options', 'SAMEORIGIN'))
	return res

@view_config(route_name='core.file.mount', permission='FILES_LIST')
def file_mnt(request):
	ff_id = request.matchdict.get('ffid')
	if ff_id == 'root':
		if not request.user.root_readable:
			raise HTTPForbidden()
		resp = DAVMountResponse(
			request=request,
			path='/',
			username=request.user.login
		)
	else:
		try:
			ff_id = int(ff_id)
		except (TypeError, ValueError):
			raise HTTPNotFound()
		sess = DBSession()
		ff = sess.query(FileFolder).get(ff_id)
		if not ff.allow_traverse(request):
			raise HTTPForbidden()
		path = '/'.join(ff.get_uri()[1:] + [''])
		resp = DAVMountResponse(
			request=request,
			path=path,
			username=request.user.login
		)
	resp.make_body()
	resp.headerlist.append(('X-Frame-Options', 'SAMEORIGIN'))
	return resp

@view_config(route_name='core.export', permission='USAGE')
def data_export(request):
	moddef = request.matchdict.get('module')
	objcls = request.matchdict.get('model')
	if (not moddef) or (not objcls):
		return HTTPNotFound()
	mmgr = request.registry.getUtility(IModuleManager)
	mb = mmgr.get_module_browser()
	if moddef not in mb:
		return HTTPNotFound()
	mod = mb[moddef]
	if objcls not in mod:
		return HTTPNotFound()
	model = mod[objcls]
	if model.export_view is None:
		return HTTPForbidden()
	rcap = model.cap_read
	if rcap and (not has_permission(rcap, request.context, request)):
		return HTTPForbidden()
	csrf = request.POST.get('csrf')
	fmt = request.POST.get('format')
	params = request.POST.get('params')
	if (not csrf) or (csrf != request.get_csrf()):
		return HTTPForbidden()
	if not fmt:
		raise ValueError('No export format specified')
	fmt = mmgr.get_export_format(fmt)
	return fmt.export(model, json.loads(params), request)

@extdirect_method('User', 'get_chpass_wizard', request_as_last_param=True, permission='USAGE', session_checks=False)
def dyn_user_chpass_wizard(request):
	sess = DBSession()
	loc = get_localizer(request)
	model = ExtModel(User)
	user = request.user
	wiz = Wizard(
		Step(
			ExtJSWizardField({
				'xtype'      : 'passwordfield',
				'name'       : 'oldpass',
				'allowBlank' : False,
				'triggers'   : None,
				'fieldLabel' : loc.translate(_('Old password')),
				'maxLength'  : 255,
				'value'      : '',
				'emptyValue' : ''
			}),
			ExtJSWizardField({
				'xtype'      : 'passwordfield',
				'name'       : 'newpass1',
				'allowBlank' : False,
				'triggers'   : None,
				'fieldLabel' : loc.translate(_('New password')),
				'maxLength'  : 255,
				'value'      : '',
				'emptyValue' : ''
			}),
			ExtJSWizardField({
				'xtype'      : 'passwordfield',
				'name'       : 'newpass2',
				'allowBlank' : False,
				'triggers'   : None,
				'fieldLabel' : loc.translate(_('Repeat password')),
				'maxLength'  : 255,
				'value'      : '',
				'emptyValue' : ''
			})
		),
		validator='ChangePassword'
	)
	return {
		'success' : True,
		'fields'  : wiz.get_cfg(model, request, use_defaults=True),
		'title'   : loc.translate(_('Change your password'))
	}

@extdirect_method('User', 'change_password', request_as_last_param=True, permission='USAGE', session_checks=False)
def dyn_user_chpass_submit(values, request):
	user = request.user
	cfg = request.registry.settings
	hash_con = cfg.get('netprofile.auth.hash', 'sha1')
	salt_len = int(cfg.get('netprofile.auth.salt_length', 4))
	old_pass = values.get('oldpass')
	new_pass1 = values.get('newpass1')
	new_pass2 = values.get('newpass2')
	if (not old_pass) or (not user.check_password(old_pass, hash_con, salt_len)):
		raise ValueError('Old password is invalid')
	if (not new_pass1) or (not new_pass2) or (new_pass1 != new_pass2):
		raise ValueError('New password is invalid')
	secpol = user.effective_policy
	if secpol:
		if secpol.check_new_password(request, user, new_pass1, dt.datetime.now()) is not True:
			raise ValueError('New password is invalid')
	user.change_password(new_pass1, values, request)

	return {
		'success' : True,
		'action'  : { 'exec' : 'afterSubmit' }
	}

@register_hook('core.validators.ChangePassword')
def dyn_user_chpass_validate(ret, values, request):
	loc = get_localizer(request)
	errors = defaultdict(list)
	user = request.user
	cfg = request.registry.settings
	hash_con = cfg.get('netprofile.auth.hash', 'sha1')
	salt_len = int(cfg.get('netprofile.auth.salt_length', 4))
	old_pass = values.get('oldpass')
	new_pass1 = values.get('newpass1')
	new_pass2 = values.get('newpass2')
	if (not old_pass) or (not user.check_password(old_pass, hash_con, salt_len)):
		errors['oldpass'].append(loc.translate(_('Old password is invalid.')))
	if not new_pass1:
		errors['newpass1'].append(loc.translate(_('New password can\'t be empty.')))
	if not new_pass2:
		errors['newpass2'].append(loc.translate(_('New password can\'t be empty.')))
	if new_pass1 != new_pass2:
		errors['newpass2'].append(loc.translate(_('Entered passwords differ.')))
	if new_pass1:
		secpol = user.effective_policy
		if secpol:
			checkpw = secpol.check_new_password(request, user, new_pass1, dt.datetime.now())
			if checkpw is not True:
				errors['newpass1'].extend(secpol_errors(checkpw, loc))
	ret['errors'].update(errors)

def dpane_simple(model, request):
	tabs = []
	request.run_hook(
		'core.dpanetabs.%s.%s' % (model.__parent__.moddef, model.name),
		tabs, model, request
	)
	cont = {
		'border' : False,
		'layout' : {
			'type'    : 'hbox',
			'align'   : 'stretch',
			'padding' : 0
		},
		'items' : [{
			'xtype'   : 'npform',
			'flex'    : 2,
			'padding' : '4 0 4 4'
		}]
	}
	if len(tabs) > 0:
		cont['items'].extend(({
			'xtype'   : 'splitter'
		}, {
			'xtype'   : 'tabpanel',
			'cls'     : 'np-subtab',
			'border'  : False,
			'flex'    : 3,
			'items'   : tabs
		}))
	else:
		cont['items'][0].update({
			'padding'  : '4',
			'defaults' : {
				'anchor' : '50%'
			}
		})
	request.run_hook(
		'core.dpane.%s.%s' % (model.__parent__.moddef, model.name),
		cont, model, request
	)
	return cont

def dpane_wide_content(model, request):
	loc = get_localizer(request)
	tabs = [{
		'xtype'   : 'npform',
		'iconCls' : 'ico-props',
		'border'  : True,
		'padding' : '4',
		'title'   : loc.translate(_('Properties'))
	}]
	request.run_hook(
		'core.dpanetabs.%s.%s' % (model.__parent__.moddef, model.name),
		tabs, model, request
	)
	cont = {
		'xtype'  : 'tabpanel',
		'cls'    : 'np-subtab',
		'border' : False,
		'items'  : tabs
	}
	request.run_hook(
		'core.dpane.%s.%s' % (model.__parent__.moddef, model.name),
		cont, model, request
	)
	if len(cont['items']) == 1:
		cont['layout'] = 'fit'
		del cont['xtype']
		del cont['cls']
		del cont['items'][0]['title']
		del cont['items'][0]['iconCls']
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

@extdirect_method('CustomValidator', 'validate', request_as_last_param=True, permission='USAGE', session_checks=False)
def custom_valid(name, values, request):
	ret = {
		'success' : True,
		'errors'  : {}
	}
	request.run_hook(
		'core.validators.%s' % str(name),
		ret, values, request
	)
	return ret

@extdirect_method('MenuTree', 'folders_read', request_as_last_param=True, permission='FILES_LIST')
def ff_tree(params, request):
	"""
	ExtDirect method used for VFS tree.
	"""

	recs = []
	sess = DBSession()

	# TODO: check chroot bounds
	# TODO: check file permissions
	u = request.user
	q = sess.query(FileFolder)
	if params['node'] == 'root':
		folder = u.group.effective_root_folder
		if folder and (not folder.can_read(u)):
			raise ValueError('Folder access denied')
		q = q.filter(FileFolder.parent == folder)
	else:
		folder = q.filter(FileFolder.id == int(params['node'])).one()
		if folder and ((not folder.can_read(u)) or (not folder.can_traverse_path(u))):
			raise ValueError('Folder access denied')
		root_ff = u.group.effective_root_folder
		if root_ff and (not folder.is_inside(root_ff)):
			raise ValueError('Folder access denied')
		q = q.filter(FileFolder.parent_id == int(params['node']))
	for ff in q:
		parent_wr = False
		if ff.parent:
			parent_wr = ff.parent.can_write(u)
		else:
			parent_wr = u.root_writable
		mi = {
			'id'             : ff.id,
			'text'           : ff.name,
			'xhandler'       : 'NetProfile.controller.FileBrowser',
			'expanded'       : False,
			'allow_read'     : ff.can_read(u),
			'allow_write'    : ff.can_write(u),
			'allow_traverse' : ff.can_traverse(u),
			'parent_write'   : parent_wr
		}
		recs.append(mi)

	return {
		'success' : True,
		'records' : recs,
		'total'   : len(recs)
	}

@extdirect_method('MenuTree', 'folders_update', request_as_last_param=True, permission='FILES_EDIT')
def ff_tree_update(params, request):
	sess = DBSession()
	user = request.user
	root_ff = user.group.effective_root_folder
	for rec in params.get('records', ()):
		ff_id = rec.get('id')
		if ff_id == 'root':
			continue
		ff_id = int(ff_id)
		ff_name = rec.get('text')
		ff_parent = rec.get('parentId')
		# TODO: support changing uid/gid and rights, maybe?
		if not ff_name:
			raise ValueError('Empty folder names are not supported')
		if ff_parent and (ff_parent != 'root'):
			ff_parent = int(ff_parent)
		else:
			ff_parent = None

		ff = sess.query(FileFolder).get(ff_id)
		if ff is None:
			raise KeyError('Unknown folder ID %d' % ff_id)

		if root_ff and (not ff.is_inside(root_ff)):
			raise ValueError('Folder access denied')
		cur_parent = ff.parent
		if cur_parent and ((not cur_parent.can_write(user)) or (not cur_parent.can_traverse_path(user))):
			raise ValueError('Folder access denied')

		ff.name = ff_name

		if ff_parent:
			new_parent = sess.query(FileFolder).get(ff_parent)
			if new_parent is None:
				raise KeyError('Unknown parent folder ID %d' % ff_parent)
			if (not new_parent.can_write(user)) or (not new_parent.can_traverse_path(user)):
				raise ValueError('Folder access denied')
			if root_ff and (not new_parent.is_inside(root_ff)):
				raise ValueError('Folder access denied')
			if new_parent.is_inside(ff):
				raise ValueError('Folder loop detected')
			ff.parent = new_parent
		elif not user.root_writable:
			raise ValueError('Folder access denied')
		else:
			ff.parent = None

	return {
		'success' : True
	}

@extdirect_method('MenuTree', 'folders_create', request_as_last_param=True, permission='FILES_CREATE')
def ff_tree_create(params, request):
	recs = []
	sess = DBSession()
	user = request.user
	total = 0
	for rec in params.get('records', ()):
		ff_name = rec.get('text')
		ff_parent = rec.get('parentId')
		# TODO: support changing uid/gid and rights, maybe?
		if not ff_name:
			raise ValueError('Empty folder names are not supported')
		if ff_parent and (ff_parent != 'root'):
			ff_parent = int(ff_parent)
		else:
			ff_parent = None

		ff = FileFolder(user=user, group=user.group)
		ff.name = ff_name
		root_ff = user.group.effective_root_folder
		if root_ff and (ff_parent is None):
			raise ValueError('Folder access denied')
		if ff_parent:
			ffp = sess.query(FileFolder).get(ff_parent)
			if ffp is None:
				raise KeyError('Unknown parent folder ID %d' % ff_parent)
			if (not ffp.can_write(user)) or (not ffp.can_traverse_path(user)):
				raise ValueError('Folder access denied')
			if root_ff and (not ffp.is_inside(root_ff)):
				raise ValueError('Folder access denied')
			ff.parent = ffp
		elif not user.root_writable:
			raise ValueError('Folder access denied')

		sess.add(ff)
		sess.flush()
		recs.append({
			'id'             : str(ff.id),
			'parentId'       : str(ff.parent.id) if ff.parent else 'root',
			'text'           : ff.name,
			'xhandler'       : 'NetProfile.controller.FileBrowser',
			'allow_read'     : ff.can_read(user),
			'allow_write'    : ff.can_write(user),
			'allow_traverse' : ff.can_traverse(user),
			'parent_write'   : ff.parent.can_write(user) if ff.parent else user.root_writable
		})
		total += 1
	return {
		'success' : True,
		'records' : recs,
		'total'   : total
	}

@extdirect_method('MenuTree', 'folders_delete', request_as_last_param=True, permission='FILES_DELETE')
def ff_tree_delete(params, request):
	sess = DBSession()
	user = request.user
	root_ff = user.group.effective_root_folder
	total = 0
	for rec in params.get('records', ()):
		ff_id = rec.get('id')
		if ff_id == 'root':
			continue
		ff_id = int(ff_id)
		ff = sess.query(FileFolder).get(ff_id)
		if ff is None:
			raise KeyError('Unknown folder ID %d' % ff_id)

		if root_ff and (not ff.is_inside(root_ff)):
			raise ValueError('Folder access denied')
		cur_parent = ff.parent
		if cur_parent and ((not cur_parent.can_write(user)) or (not cur_parent.can_traverse_path(user))):
			raise ValueError('Folder access denied')
		if (not cur_parent) and (not user.root_writable):
			raise ValueError('Folder access denied')

		# Extra precaution
		if ff.user != user:
			raise ValueError('Folder access denied')

		sess.delete(ff)
		total += 1
	return {
		'success' : True,
		'total'   : total
	}

@extdirect_method('MenuTree', 'settings_read', request_as_last_param=True, permission='USAGE')
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
		'records' : menu,
		'total'   : len(menu)
	}

@extdirect_method('MenuTree', 'users_read', request_as_last_param=True, permission='USAGE')
def menu_users(params, request):
	"""
	ExtDirect method for users menu tree.
	"""

	menu = []
	sess = DBSession()

	for user in sess.query(User)\
			.filter(User.enabled == True, User.state == UserState.active)\
			.order_by(User.login):
		mi = {
			'id'      : 'user-%d' % user.id,
			'text'    : user.login,
			'leaf'    : True,
			'iconCls' : 'ico-status-offline'
		}
		menu.append(mi)

	return {
		'success' : True,
		'records' : menu,
		'total'   : len(menu)
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

@extdirect_method('Privilege', 'group_get', request_as_last_param=True, permission='GROUPS_GETCAP')
def dyn_priv_group_get(params, request):
	"""
	ExtDirect method for getting group's capabilities.
	"""

	gid = int(params.get('owner'))
	if gid <= 0:
		raise KeyError('Invalid group ID')
	recs = []
	sess = DBSession()
	group = sess.query(Group).get(gid)
	if group is None:
		raise KeyError('Invalid group ID')

	for priv in sess.query(Privilege)\
			.join(NPModule)\
			.filter(NPModule.enabled == True, Privilege.can_be_set == True)\
			.order_by(Privilege.name):
		prx = {
			'privid'  : priv.id,
			'owner'   : group.id,
			'code'    : priv.code,
			'name'    : priv.name,
			'hasacls' : priv.has_acls,
			'value'   : None
		}
		if priv.code in group.caps:
			prx['value'] = group.caps[priv.code].value
		recs.append(prx)

	return {
		'records' : recs,
		'total'   : len(recs),
		'success' : True
	}

@extdirect_method('Privilege', 'group_set', request_as_last_param=True, permission='GROUPS_SETCAP')
def dyn_priv_group_set(px, request):
	"""
	ExtDirect method for setting group's capabilities.
	"""

	if 'records' not in px:
		raise ValueError('No records found')
	sess = DBSession()
	for params in px['records']:
		gid = int(params.get('owner'))
		privid = int(params.get('privid'))
		value = params.get('value')
		if gid <= 0:
			raise KeyError('Invalid group ID')
		group = sess.query(Group).get(gid)
		if group is None:
			raise KeyError('Invalid group ID')
		if value not in {True, False, None}:
			raise ValueError('Invalid capability value')
		priv = sess.query(Privilege)\
			.join(NPModule)\
			.filter(Privilege.id == privid, NPModule.enabled == True, Privilege.can_be_set == True)\
			.one()
		code = priv.code

		if value is None:
			if code in group.privileges:
				del group.privileges[code]
		else:
			group.privileges[code] = value

	return { 'success' : True }

@extdirect_method('ACL', 'group_get', request_as_last_param=True, permission='GROUPS_GETACL')
def dyn_acl_group_get(params, request):
	"""
	ExtDirect method for getting group's ACLs.
	"""

	gid = int(params.get('owner'))
	if gid <= 0:
		raise KeyError('Invalid group ID')
	code = params.get('code')
	recs = []
	sess = DBSession()
	group = sess.query(Group).get(gid)
	if group is None:
		raise KeyError('Invalid group ID')
	priv = sess.query(Privilege)\
		.join(NPModule)\
		.filter(Privilege.code == code, NPModule.enabled == True, Privilege.can_be_set == True)\
		.one()
	acls = priv.get_acls()
	if acls is None:
		raise ValueError('Invalid privilege type')

	for aid, aname in acls.items():
		prx = {
			'privid'  : aid,
			'owner'   : group.id,
			'code'    : priv.code,
			'name'    : aname,
			'hasacls' : False,
			'value'   : None
		}
		if (priv.code, aid) in group.acls:
			prx['value'] = group.acls[(priv.code, aid)]
		recs.append(prx)

	return {
		'records' : recs,
		'total'   : len(recs),
		'success' : True
	}

@extdirect_method('ACL', 'group_set', request_as_last_param=True, permission='GROUPS_SETACL')
def dyn_acl_group_set(px, request):
	"""
	ExtDirect method for setting group's ACLs.
	"""

	if 'records' not in px:
		raise ValueError('No records found')
	sess = DBSession()
	for params in px['records']:
		gid = int(params.get('owner'))
		aclid = int(params.get('privid'))
		code = params.get('code')
		value = params.get('value')
		if gid <= 0:
			raise KeyError('Invalid group ID')
		group = sess.query(Group).get(gid)
		if group is None:
			raise KeyError('Invalid group ID')
		if value not in {True, False, None}:
			raise ValueError('Invalid capability value')
		priv = sess.query(Privilege)\
			.join(NPModule)\
			.filter(Privilege.code == code, NPModule.enabled == True, Privilege.can_be_set == True)\
			.one()
		code = priv.code

		if value is None:
			if (code, aclid) in group.acls:
				del group.acls[(code, aclid)]
		else:
			group.acls[(code, aclid)] = value

	return { 'success' : True }

@extdirect_method('Privilege', 'user_get', request_as_last_param=True, permission='USERS_GETCAP')
def dyn_priv_user_get(params, request):
	"""
	ExtDirect method for getting user's capabilities.
	"""

	uid = int(params.get('owner'))
	if uid <= 0:
		raise KeyError('Invalid user ID')
	recs = []
	sess = DBSession()
	user = sess.query(User).get(uid)
	if user is None:
		raise KeyError('Invalid user ID')

	for priv in sess.query(Privilege)\
			.join(NPModule)\
			.filter(NPModule.enabled == True, Privilege.can_be_set == True)\
			.order_by(Privilege.name):
		prx = {
			'privid'  : priv.id,
			'owner'   : user.id,
			'code'    : priv.code,
			'name'    : priv.name,
			'hasacls' : priv.has_acls,
			'value'   : None
		}
		if priv.code in user.caps:
			prx['value'] = user.caps[priv.code].value
		recs.append(prx)

	return {
		'records' : recs,
		'total'   : len(recs),
		'success' : True
	}

@extdirect_method('Privilege', 'user_set', request_as_last_param=True, permission='USERS_SETCAP')
def dyn_priv_user_set(px, request):
	"""
	ExtDirect method for setting user's capabilities.
	"""

	if 'records' not in px:
		raise ValueError('No records found')
	sess = DBSession()
	for params in px['records']:
		uid = int(params.get('owner'))
		privid = int(params.get('privid'))
		value = params.get('value')
		if uid <= 0:
			raise KeyError('Invalid user ID')
		user = sess.query(User).get(uid)
		if user is None:
			raise KeyError('Invalid user ID')
		if value not in {True, False, None}:
			raise ValueError('Invalid capability value')
		priv = sess.query(Privilege)\
			.join(NPModule)\
			.filter(Privilege.id == privid, NPModule.enabled == True, Privilege.can_be_set == True)\
			.one()
		code = priv.code

		if value is None:
			if code in user.privileges:
				del user.privileges[code]
		else:
			user.privileges[code] = value

	return { 'success' : True }

@extdirect_method('ACL', 'user_get', request_as_last_param=True, permission='USERS_GETACL')
def dyn_acl_user_get(params, request):
	"""
	ExtDirect method for getting user's ACLs.
	"""

	uid = int(params.get('owner'))
	if uid <= 0:
		raise KeyError('Invalid user ID')
	code = params.get('code')
	recs = []
	sess = DBSession()
	user = sess.query(User).get(uid)
	if user is None:
		raise KeyError('Invalid user ID')
	priv = sess.query(Privilege)\
		.join(NPModule)\
		.filter(Privilege.code == code, NPModule.enabled == True, Privilege.can_be_set == True)\
		.one()
	acls = priv.get_acls()
	if acls is None:
		raise ValueError('Invalid privilege type')

	for aid, aname in acls.items():
		prx = {
			'privid'  : aid,
			'owner'   : user.id,
			'code'    : priv.code,
			'name'    : aname,
			'hasacls' : False,
			'value'   : None
		}
		if (priv.code, aid) in user.acls:
			prx['value'] = user.acls[(priv.code, aid)]
		recs.append(prx)

	return {
		'records' : recs,
		'total'   : len(recs),
		'success' : True
	}

@extdirect_method('ACL', 'user_set', request_as_last_param=True, permission='USERS_SETACL')
def dyn_acl_user_set(px, request):
	"""
	ExtDirect method for setting user's ACLs.
	"""

	if 'records' not in px:
		raise ValueError('No records found')
	sess = DBSession()
	for params in px['records']:
		uid = int(params.get('owner'))
		aclid = int(params.get('privid'))
		code = params.get('code')
		value = params.get('value')
		if uid <= 0:
			raise KeyError('Invalid user ID')
		user = sess.query(User).get(uid)
		if user is None:
			raise KeyError('Invalid user ID')
		if value not in {True, False, None}:
			raise ValueError('Invalid capability value')
		priv = sess.query(Privilege)\
			.join(NPModule)\
			.filter(Privilege.code == code, NPModule.enabled == True, Privilege.can_be_set == True)\
			.one()
		code = priv.code

		if value is None:
			if (code, aclid) in user.acls:
				del user.acls[(code, aclid)]
		else:
			user.acls[(code, aclid)] = value

	return { 'success' : True }

@register_hook('core.dpanetabs.core.Group')
def _dpane_group_caps(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Privileges')),
		'iconCls'           : 'ico-mod-privilege',
		'xtype'             : 'capgrid',
		'stateId'           : None,
		'stateful'          : False,
		'apiGet'            : 'NetProfile.api.Privilege.group_get',
		'apiSet'            : 'NetProfile.api.Privilege.group_set'
	})

@register_hook('core.dpanetabs.core.User')
def _dpane_user_caps(tabs, model, req):
	loc = get_localizer(req)
	tabs.extend(({
		'title'             : loc.translate(_('Phones')),
		'iconCls'           : 'ico-mod-userphone',
		'xtype'             : 'grid_core_UserPhone',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('user',),
		'extraParamProp'    : 'uid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('E-mail')),
		'iconCls'           : 'ico-mod-useremail',
		'xtype'             : 'grid_core_UserEmail',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('user',),
		'extraParamProp'    : 'uid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Communications')),
		'iconCls'           : 'ico-mod-usercommunicationchannel',
		'xtype'             : 'grid_core_UserCommunicationChannel',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('user',),
		'extraParamProp'    : 'uid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Privileges')),
		'iconCls'           : 'ico-mod-privilege',
		'xtype'             : 'capgrid',
		'stateId'           : None,
		'stateful'          : False,
		'apiGet'            : 'NetProfile.api.Privilege.user_get',
		'apiSet'            : 'NetProfile.api.Privilege.user_set'
	}))

_cal_serial = 1
def generate_calendar(name, color):
	global _cal_serial
	cal = {
		'id'    : 'system-%u' % _cal_serial,
		'title' : name,
		'owner' : 'SYSTEM',
		'color' : color
	}
	_cal_serial += 1
	if _cal_serial >= 100:
		raise ValueError('Too many system calendars')
	return cal

@extdirect_method('Calendar', 'cal_read', request_as_last_param=True, permission='USAGE')
def cals_read(params, req):
	cals = []
	loc = get_localizer(req)
	req.run_hook('core.calendar.calendars.read', cals, params, req)
	for cal in cals:
		if 'title' in cal:
			cal['title'] = loc.translate(cal['title'])
	sess = DBSession()
	my_login = str(req.user)
	for cal in sess.query(Calendar).filter(Calendar.user_id == req.user.id):
		cals.append({
			'id'        : 'user-%u' % cal.id,
			'title'     : cal.name,
			'desc'      : cal.description,
			'owner'     : my_login,
			'color'     : cal.style,
			'hidden'    : False,
			'cancreate' : True
		})
	for cali in sess.query(CalendarImport).filter(CalendarImport.user_id == req.user.id):
		cal = cali.calendar
		if not cal.can_read(req.user):
			continue
		cals.append({
			'id'        : 'user-%u' % cal.id,
			'title'     : cali.real_name,
			'desc'      : cal.description,
			'owner'     : str(cal.user),
			'color'     : cali.style or cal.style,
			'hidden'    : False,
			'cancreate' : cal.can_write(req.user)
		})
	return {
		'success'   : True,
		'calendars' : cals,
		'total'     : len(cals)
	}

@extdirect_method('Calendar', 'cal_avail', request_as_last_param=True, permission='USAGE')
def cals_avail(params, req):
	cals = []
	sess = DBSession()
	q = sess.query(Calendar).filter(
		Calendar.user_id != req.user.id,
		or_(
			and_(Calendar.group_access != CalendarAccess.none, Calendar.group == req.user.group),
			Calendar.global_access != CalendarAccess.none
		)
	)
	for cal in q:
		cals.append({
			'id'        : 'user-%u' % cal.id,
			'title'     : cal.name,
			'desc'      : cal.description,
			'owner'     : str(cal.user),
			'color'     : cal.style,
			'hidden'    : False,
			'cancreate' : cal.can_write(req.user)
		})
	return {
		'success'   : True,
		'calendars' : cals,
		'total'     : len(cals)
	}

@extdirect_method('Calendar', 'evt_read', request_as_last_param=True, permission='USAGE')
def evts_read(params, req):
	logger.debug('Running calendar read op: %r' % (params,))
	evts = []
	req.run_hook('core.calendar.events.read', evts, params, req)
	return {
		'success' : True,
		'evts'    : evts,
		'total'   : len(evts)
	}

@extdirect_method('Calendar', 'evt_update', request_as_last_param=True, permission='USAGE')
def evts_update(params, req):
	logger.debug('Running calendar update op: %r' % (params,))
	req.run_hook('core.calendar.events.update', params, req)
	return { 'success' : True }

@extdirect_method('Calendar', 'evt_create', request_as_last_param=True, permission='USAGE')
def evts_create(params, req):
	logger.debug('Running calendar create op: %r' % (params,))
	req.run_hook('core.calendar.events.create', params, req)
	return { 'success' : True }

@extdirect_method('Calendar', 'evt_delete', request_as_last_param=True, permission='USAGE')
def evts_delete(params, req):
	logger.debug('Running calendar delete op: %r' % (params,))
	req.run_hook('core.calendar.events.delete', params, req)
	return { 'success' : True }

@register_hook('core.calendar.events.read')
def _cal_events(evts, params, req):
	ts_from = params.get('startDate')
	ts_to = params.get('endDate')
	if (not ts_from) or (not ts_to):
		return
	cals = params.get('cals')
	if isinstance(cals, Iterable) and len(cals):
		try:
			cals = [int(cal[5:]) for cal in cals if cal[:5] == 'user-']
		except (TypeError, ValueError):
			cals = ()
		if len(cals) == 0:
			return
	else:
		cals = None
	ts_from = dparse(ts_from).replace(hour=0, minute=0, second=0, microsecond=0)
	ts_to = dparse(ts_to).replace(hour=23, minute=59, second=59, microsecond=999999)
	sess = DBSession()
	cal_q = sess.query(Calendar).filter(Calendar.user == req.user)
	if cals:
		cal_q = cal_q.filter(Calendar.id.in_(cals))
	cal_ids = [cal.id for cal in cal_q]
	for cali in sess.query(CalendarImport).filter(CalendarImport.user_id == req.user.id):
		cal = cali.calendar
		if cal.user == req.user:
			continue
		if cals and (cal.id not in cals):
			continue
		if not cal.can_read(req.user):
			continue
		if cal.id in cal_ids:
			continue
		cal_ids.append(cal.id)
	q = sess.query(Event)\
		.filter(
			Event.calendar_id.in_(cal_ids),
			Event.event_start <= ts_to,
			Event.event_end >= ts_from
		)
	for e in q:
		ev = {
			'id'       : 'event-%u' % e.id,
			'cid'      : 'user-%u' % e.calendar_id,
			'title'    : e.summary,
			'start'    : e.event_start,
			'end'      : e.event_end,
			'ad'       : e.all_day,
			'notes'    : e.description,
			'loc'      : e.location,
			'url'      : e.url,
			'caned'    : e.calendar.can_write(req.user)
		}
		evts.append(ev)

def _ev_set(sess, ev, params, req):
	user = req.user
	if ev.id:
		if (not ev.calendar) or (not ev.calendar.can_write(user)):
			return False
	cal_id = params.get('CalendarId', '')
	if cal_id:
		if cal_id[:5] != 'user-':
			return False
		try:
			cal_id = int(cal_id[5:])
		except (TypeError, ValueError):
			return False
		cal = sess.query(Calendar).get(cal_id)
		if (cal is None) or (not cal.can_write(user)):
			return False
		ev.calendar = cal

	val = params.get('Title', False)
	if val:
		ev.summary = val
	val = params.get('Url', False)
	if val:
		ev.url = val
	val = params.get('Notes', False)
	if val:
		ev.description = val
	val = params.get('Location', False)
	if val:
		ev.location = val
	if 'StartDate' in params:
		new_ts = dparse(params['StartDate']).replace(tzinfo=None, microsecond=0)
		if new_ts:
			ev.event_start = new_ts
	if 'EndDate' in params:
		new_ts = dparse(params['EndDate']).replace(tzinfo=None, microsecond=0)
		if new_ts:
			ev.event_end = new_ts
	val = params.get('IsAllDay', None)
	if isinstance(val, bool):
		ev.all_day = val
		# FIXME: enforce proper times for all-day events
	return True

@register_hook('core.calendar.events.update')
def _cal_events_update(params, req):
	if 'EventId' not in params:
		return
	evtype, evid = params['EventId'].split('-')
	if evtype != 'event':
		return
	evid = int(evid)
	sess = DBSession()
	ev = sess.query(Event).get(evid)
	if ev is None:
		return False
	if not _ev_set(sess, ev, params, req):
		return False
	return True

@register_hook('core.calendar.events.create')
def _cal_events_create(params, req):
	sess = DBSession()
	ev = Event()
	ev.creation_time = dt.datetime.now()
	if not _ev_set(sess, ev, params, req):
		del ev
		return False
	ev.user = req.user
	sess.add(ev)
	return True

@register_hook('core.calendar.events.delete')
def _cal_events_delete(params, req):
	if 'EventId' not in params:
		return
	evtype, evid = params['EventId'].split('-')
	if evtype != 'event':
		return
	evid = int(evid)
	sess = DBSession()
	ev = sess.query(Event).get(evid)
	if ev is None:
		return False
	if (not ev.calendar) or (not ev.calendar.can_write(req.user)):
		return False
	sess.delete(ev)
	return True

@register_hook('core.validators.ImportCalendar')
def import_calendar_validator(ret, values, request):
	loc = get_localizer(request)
	errors = defaultdict(list)
	if ('caldef' not in values) or (values['caldef'][:5] != 'user-'):
		errors['caldef'].append(loc.translate(_('Invalid calendar selected.')))
	else:
		try:
			cal_id = int(values['caldef'][5:])
		except (TypeError, ValueError):
			errors['caldef'].append(loc.translate(_('Invalid calendar selected.')))
		else:
			sess = DBSession()
			cal = sess.query(Calendar).get(cal_id)
			if (not cal) or (not cal.can_read(request.user)):
				errors['caldef'].append(loc.translate(_('Invalid calendar selected.')))
			else:
				cnt = sess.query(func.count('*')).select_from(CalendarImport).filter(
					CalendarImport.user == request.user,
					CalendarImport.calendar == cal
				).scalar()
				if cnt > 0:
					errors['caldef'].append(loc.translate(_('You have already imported this calendar.')))
	ret['errors'].update(errors)

@register_hook('np.menu')
def _menu_custom(name, menu, req, extb):
	if name != 'modules':
		return
	loc = get_localizer(req)
	menu.append({
		'leaf'     : False,
		'expanded' : True,
		'xview'    : 'calendar',
		'iconCls'  : 'ico-mod-calendar',
		'text'     : loc.translate(_('Events')),
		'id'       : 'event',
		'children' : ({
			'leaf'    : True,
			'xview'   : 'grid_core_Calendar',
			'text'    : loc.translate(_('My Calendars')),
			'id'      : 'calendars',
			'iconCls' : 'ico-mod-calendars'
		}, {
			'leaf'    : True,
			'xview'   : 'grid_core_CalendarImport',
			'text'    : loc.translate(_('Other Calendars')),
			'id'      : 'calendarimports',
			'iconCls' : 'ico-mod-calendarimport'
		})
	})

