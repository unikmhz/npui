#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: ExtDirect server
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
#
# Largely based on Igor Stroh's pyramid_extdirect
# See http://github.com/jenner/pyramid_extdirect

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from collections import defaultdict
import json
import traceback
import datetime as dt
import decimal
from dateutil.tz import tzlocal

from pyramid.security import has_permission
from pyramid.view import render_view_to_response
from pyramid.threadlocal import get_current_request
from webob import Response
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.interfaces import ComponentLookupError
import venusian

from netprofile.ext.data import ExtModel
from netprofile.common.modules import IModuleManager
from netprofile.common.hooks import register_hook
from netprofile.common.factory import RootFactory
from netprofile.common import ipaddr

# form parameters sent by ExtDirect when using a form-submit
# see http://www.sencha.com/products/js/direct.php
FORM_DATA_KEYS = frozenset([
	'extAction',
	'extMethod',
	'extTID',
	'extUpload',
	'extType'
])

# response to a file upload cannot be return as application/json, ExtDirect
# defines a special html response body for this use case where the response
# data is added to a textarea for faster JS-side decoding (since textarea text
# is not a DOM node)
FORM_SUBMIT_RESPONSE_TPL = '<html><body><textarea>%s</textarea></body></html>'

def get_ext_csrf(request):
	return request.headers.get('X-CSRFToken', '')

def _mk_cb_key(action_name, method_name):
	""" helper function to create a unique actions dict key """
	return action_name + '#' + method_name

class JsonReprEncoder(json.JSONEncoder):
	"""
	A convenience wrapper for classes that support __json__().
	"""
	def default(self, obj):
		if isinstance(obj, Response) and obj.content_type == 'application/json':
			# return decoded response body in case it's an already
			# rendered exception view
			return json.loads(obj.unicode_body)
		jr = getattr(obj, '__json__', None)
		if jr is not None:
			return jr()
		if isinstance(obj, dt.datetime):
			if obj.tzinfo is None:
				obj = obj.replace(tzinfo=tzlocal())
			return obj.isoformat()
		if isinstance(obj, dt.date):
			return obj.isoformat()
		if isinstance(obj, dt.time):
			return obj.isoformat()
		if isinstance(obj, ipaddr.IPv4Address):
			return int(obj)
		if isinstance(obj, ipaddr.IPv6Address):
			return tuple(obj.packed)
		if isinstance(obj, decimal.Decimal):
			return str(obj)

		return super(JsonReprEncoder, self).default(obj)

class IExtDirectRouter(Interface):
	"""
	Marker interface for ExtDirectRouter utility.
	"""
	pass

class AccessDeniedException(Exception):
	"""
	Marker exception for failed permission checks.
	"""
	pass

@implementer(IExtDirectRouter)
class ExtDirectRouter(object):
	"""
	Handles ExtDirect API respresentation and routing.

	The ExtDirectRouter accepts a number of arguments: ``app``,
	``api_path``, ``router_path``, ``namespace``, ``descriptor``
	and ``expose_exceptions``.

	The ``app`` argument is a python package or module used
	which is used to scan for ``extdirect_method`` decorated
	functions/methods once the API is built.

	The ``api_path`` and ``router_path`` arguments are the
	paths/URIs of pyramid views. ``api_path`` renders
	the ExtDirect API, ``router_path`` is the routing endpoint
	for ExtDirect calls.

	If the ``namespace`` argument is passed it will be used in
	the API as Ext namespace (default is 'Ext.app').

	If the ``descriptor`` argument is passed it's used as ExtDirect
	API descriptor name (default is Ext.app.REMOTING_API).

	If ``expose_exceptions`` argument is set to True the exception
	traceback will be exposed in the response object. WARNING this
	is potentially dangeerous, do not use in production environments.

	The ``debug_mode`` argument will create a 'message' key in the
	response object pointing to a structure that can be used in pyramid
	debug toolbar.

	See http://www.sencha.com/products/js/direct.php for further infos.

	The optional ``expose_exceptions`` argument controls the output of
	an ExtDirect call - if ``True``, the router will provide additional
	information about exceptions.
	"""

	def __init__(self,
				api_path='direct/api',
				router_path='direct/router',
				namespace='NetProfile.api',
				descriptor='NetProfile.api.REMOTING',
				provider_id='netprofile-provider',
				expose_exceptions=True,
				debug_mode=False):
		self.api_path = api_path
		self.router_path = router_path
		self.namespace = namespace
		self.descriptor = descriptor
		self.provider_id = provider_id
		self.expose_exceptions = expose_exceptions
		self.debug_mode = debug_mode
		self.actions = defaultdict(dict)

	def add_action(self, action_name, **settings):
		"""
		Registers an action.

		``action_name``: Action name

		Possible values of `settings``:

		``method_name``: Method name
		``callback``: The callback to execute upon client request
		``numargs``: Number of arguments passed to the wrapped callable
		``accepts_files``: If true, this action will be declared as formHandler in API
		``permission``: The permission needed to execute the wrapped callable
		``request_as_last_param``: If true, the wrapped callable will receive a request object
			as last argument

		"""
		callback_key = _mk_cb_key(action_name, settings['method_name'])
		self.actions[action_name][callback_key] = settings

	def add_model(self, name, model):
		self.add_action(
			name,
			method_name='read',
			callback=model.read,
			numargs=1,
			accepts_files=False,
			request_as_last_param=True,
			permission=model.cap_read
		)
		self.add_action(
			name,
			method_name='read_one',
			callback=model.read_one,
			numargs=1,
			accepts_files=False,
			request_as_last_param=True,
			permission=model.cap_read
		)
		self.add_action(
			name,
			method_name='create',
			callback=model.create,
			numargs=1,
			accepts_files=False,
			request_as_last_param=True,
			permission=model.cap_create
		)
		self.add_action(
			name,
			method_name='update',
			callback=model.update,
			numargs=1,
			accepts_files=False,
			request_as_last_param=True,
			permission=model.cap_edit
		)
		self.add_action(
			name,
			method_name='delete',
			callback=model.delete,
			numargs=1,
			accepts_files=False,
			request_as_last_param=True,
			permission=model.cap_delete
		)
		self.add_action(
			name,
			method_name='get_fields',
			callback=model.get_fields,
			numargs=0,
			request_as_last_param=True,
			accepts_files=False,
			permission=model.cap_read
		)
		self.add_action(
			name,
			method_name='validate_fields',
			callback=model.validate_fields,
			numargs=1,
			request_as_last_param=True,
			accepts_files=False,
			permission=model.cap_read
		)
		if model.create_wizard:
			self.add_action(
				name,
				method_name='get_create_wizard',
				callback=model.get_create_wizard,
				numargs=0,
				request_as_last_param=True,
				accepts_files=False,
				permission=model.cap_read
			)
			self.add_action(
				name,
				method_name='create_wizard_action',
				callback=model.create_wizard_action,
				numargs=3,
				request_as_last_param=True,
				accepts_files=False,
				permission=model.cap_create
			)
		if model.wizards:
			self.add_action(
				name,
				method_name='get_wizard',
				callback=model.get_wizard,
				numargs=1,
				request_as_last_param=True,
				accepts_files=False,
				permission=model.cap_read
			)
			self.add_action(
				name,
				method_name='wizard_action',
				callback=model.wizard_action,
				numargs=4,
				request_as_last_param=True,
				accepts_files=False,
				permission=model.cap_create # FIXME!
			)

	def get_actions(self):
		"""
		Build and return a dict of actions to be used in ExtDirect API.
		"""
		ret = {}
		for (k, v) in list(self.actions.items()):
			items = []
			for settings in list(v.values()):
				d = dict(
					len = settings['numargs'],
					name = settings['method_name']
				)
				if settings['accepts_files']:
					d['formHandler'] = True
				items.append(d)
			ret[k] = items
		return ret

	def get_method(self, action, method):
		"""
		Return method's settings.
		"""
		if action not in self.actions:
			raise KeyError('Invalid action: ' + action)
		key = _mk_cb_key(action, method)
		if key not in self.actions[action]:
			raise KeyError("No such method in '%s': '%s'" % (action, method))
		return self.actions[action][key]

	def _get_api_dict(self, request):
		return dict(
			url = request.application_url + '/' + self.router_path,
			type = 'remoting',
			namespace = self.namespace,
			id = self.provider_id,
			actions = self.get_actions()
		)

	def dump_api(self, request):
		"""
		Dump all known remote methods.
		"""
		return """Ext.ns('%s'); %s = %s;""" % \
			(self.namespace, self.descriptor, json.dumps(self._get_api_dict(request)))

	def _do_route(self, action_name, method_name, params, trans_id, request):
		"""
		Perform routing, i.e. calls decorated methods/functions.
		"""
		if params is None:
			params = list()
		settings = self.get_method(action_name, method_name)
		permission = settings.get('permission', None)
		ret = {
			'type'   : 'rpc',
			'tid'    : trans_id,
			'action' : action_name,
			'method' : method_name,
			'result' : None
		}

		callback = settings['callback']

		append_request = settings.get('request_as_last_param', False)
		permission_ok = True
		if hasattr(callback, '__self__'):
			if isinstance(callback.__self__, ExtModel):
				instance = callback.__self__
				pinst = RootFactory(request)
				if permission is not None:
					permission_ok = has_permission(permission, pinst, request)
				else:
					permission_ok = has_permission('USAGE', pinst, request)
				if append_request:
					params.append(request)
			else:
				cls = callback.__self__.__class__
				instance = cls(request)
				params.insert(0, instance)
				if permission is not None:
					permission_ok = has_permission(permission, instance, request)
				else:
					permission_ok = has_permission('USAGE', pinst, request)
		elif append_request:
			params.append(request)

		try:
			if not permission_ok:
				raise AccessDeniedException('Access denied')
			ret['result'] = callback(*params)
		except Exception as e:
			# Let a user defined view for specific exception prevent returning
			# a server error.
			exception_view = render_view_to_response(e, request)
			if exception_view is not None:
				ret['result'] = exception_view
				return ret

			ret['type'] = 'exception'
			if self.expose_exceptions:
				ret['result'] = {
					'error'           : True,
					'message'         : str(e),
					'exception_class' : str(e.__class__),
					'stacktrace'      : traceback.format_exc()
				}
			else:
				message = 'Error executing %s.%s' % (action_name, method_name)
				ret['result'] = {
					'error'   : True,
					'message' : message
				}

			if self.debug_mode:
				# if pyramid_debugtoolbar is enabled, generate an interactive page
				# and include the url to access it in the ext direct Exception response text
				from pyramid_debugtoolbar.tbtools import get_traceback
				import sys
				exc_history = request.exc_history
				if exc_history is not None:
					tb = get_traceback(info=sys.exc_info(),
							skip=1,
							show_hidden_frames=False,
							ignore_system_exceptions=True)
					for frame in tb.frames:
						exc_history.frames[frame.id] = frame
					exc_history.tracebacks[tb.id] = tb

					qs = {
						'tb'    : str(tb.id),
						'token' : request.registry.pdtb_token
					}
					msg = 'Exception: traceback URL: %s'
					exc_url = request.route_url('debugtoolbar', subpath=('exception',), _query=qs)
					exc_msg = msg % (exc_url)
					ret['message'] = exc_msg
		return ret

	def route(self, request):
		token = request.get_csrf()
		if token != request.ext_csrf:
			raise ValueError('CSRF token didn\'t match')
		is_form_data = is_form_submit(request)
		if is_form_data:
			params = parse_extdirect_form_submit(request)
		else:
			params = parse_extdirect_request(request)
		ret = []
		for (act, meth, params, tid) in params:
			ret.append(self._do_route(act, meth, params, tid, request))
		if not is_form_data:
			if len(ret) == 1:
				ret = ret[0]
			return (json.dumps(ret, cls=JsonReprEncoder), False)
		ret = ret[0] # form data cannot be batched
		s = json.dumps(ret, cls=JsonReprEncoder).replace('&quot;', r'\&quot;');
		return (s, True)
		#return (FORM_SUBMIT_RESPONSE_TPL % (s,), True)

class extdirect_method(object):
	"""
	Enables direct ExtJS access to python methods through JSON/form submit.
	"""
	def __init__(self,
				action=None,
				method_name=None,
				permission=None,
				accepts_files=False,
				request_as_last_param=False):
		self._settings = dict(
			action = action,
			method_name = method_name,
			permission = permission,
			accepts_files = accepts_files,
			request_as_last_param = request_as_last_param,
			original_name = None
		)

	def __call__(self, wrapped):
		original_name = wrapped.__name__
		self._settings['original_name'] = original_name
		if self._settings['method_name'] is None:
			self._settings['method_name'] = original_name

		self.info = venusian.attach(
			wrapped,
			self.register,
			category='extdirect'
		)
		return wrapped

	def _get_settings(self):
		return self._settings.copy()

	def register(self, scanner, name, ob):
		settings = self._get_settings()

		class_context = isinstance(ob, type)

		if class_context:
			callback = getattr(ob, settings['original_name'])
			numargs = callback.__func__.__code__.co_argcount
			# instance var doesn't count
			numargs -= 1
		else:
			if settings['action'] is None:
				raise ValueError('Decorated function has no action (name)')
			callback = ob
			numargs = callback.__code__.co_argcount

		if numargs and settings['request_as_last_param']:
			numargs -= 1

		settings['numargs'] = numargs

		action = settings.pop('action', None)
		if action is not None:
			name = action

		if class_context:
			class_settings = getattr(ob, '__extdirect_settings__', None)
			if class_settings:
				if action is None:
					name = class_settings.get('default_action_name', name)
				if settings.get('permission') is None:
					permission = class_settings.get('default_permission')
					settings['permission'] = permission

		try:
			extdirect = scanner.config.registry.getUtility(IExtDirectRouter)
			extdirect.add_action(name, callback=callback, **settings)
		except ComponentLookupError:
			pass


def is_form_submit(request):
	"""
	Check if a request contains ExtDirect form submit.
	"""
	left_over = FORM_DATA_KEYS - set(request.params)
	return not left_over


def parse_extdirect_form_submit(request):
	"""
	Extracts ExtDirect remoting parameters from request
	which are provided by a form submission.
	"""
	params = request.params
	action = params.get('extAction')
	method = params.get('extMethod')
	tid = params.get('extTID')
	data = dict()
	for key in params:
		if key not in FORM_DATA_KEYS:
			data[key] = params[key]
	return [(action, method, [data], tid)]


def parse_extdirect_request(request):
	"""
	Extracts ExtDirect remoting parameters from request
	which are provided by an AJAX request.
	"""
	body = request.body
	decoded_body = json.loads(body.decode())
	ret = []
	if not isinstance(decoded_body, list):
		decoded_body = [decoded_body]
	for p in decoded_body:
		action = p['action']
		method = p['method']
		data = p['data']
		tid = p['tid']
		ret.append((action, method, data, tid))
	return ret


def api_view(request):
	"""
	Renders the API.
	"""
	extdirect = request.registry.getUtility(IExtDirectRouter)
	body = extdirect.dump_api(request)
	return Response(body, content_type=str('text/javascript'), charset=str('UTF-8'))


def router_view(request):
	"""
	Renders the result of an ExtDirect call.
	"""
	extdirect = request.registry.getUtility(IExtDirectRouter)
	(body, is_form_data) = extdirect.route(request)
	ctype = 'text/html' if is_form_data else 'application/json'
	return Response(body, content_type=str(ctype), charset=str('UTF-8'))

@register_hook('np.model.load')
def _proc_model(mmgr, model):
	extd = mmgr.cfg.registry.getUtility(IExtDirectRouter)
	extd.add_model(model.__name__, model)

def includeme(config):
	"""
	Let ExtDirect be included by config.include().
	"""
	config.add_request_method(get_ext_csrf, str('ext_csrf'), reify=True)
	settings = config.registry.settings
	extdirect_config = dict()
	names = (
		'api_path',
		'router_path',
		'namespace',
		'descriptor',
		'provider_id',
		'expose_exceptions',
		'debug_mode'
	)
	for name in names:
		qname = 'netprofile.ext.direct.%s' % name
		value = settings.get(qname, None)
		if name == 'expose_exceptions' or name == 'debug_mode':
			value = (value == 'true')
		if value is not None:
			extdirect_config[name] = value

	extd = ExtDirectRouter(**extdirect_config)
	config.registry.registerUtility(extd, IExtDirectRouter)

	api_view_perm = settings.get('netprofile.ext.direct.api_view_permission')
	config.add_route('extapi', extd.api_path)
	config.add_view(api_view, route_name='extapi', permission=api_view_perm)

	router_view_perm = settings.get('netprofile.ext.direct.router_view_permission')
	config.add_route('extrouter', extd.router_path)
	config.add_view(router_view, route_name='extrouter', permission=router_view_perm)

	config.scan()

