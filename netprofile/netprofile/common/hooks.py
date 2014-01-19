#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Runtime hooks support
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

__all__ = [
	'register_block',
	'register_hook'
]

from zope.interface import (
	implementer,
	Interface
)
import io
import venusian
from netprofile.tpl import TemplateObject

class IHookManager(Interface):
	pass

@implementer(IHookManager)
class HookManager(object):
	def __init__(self):
		self.hooks = {}
		self.blocks = {}

	def reg_block(self, name, cb):
		if name not in self.blocks:
			self.blocks[name] = []
		if cb not in self.blocks[name]:
			self.blocks[name].append(cb)

	def reg_hook(self, name, cb):
		if name not in self.hooks:
			self.hooks[name] = []
		if cb not in self.hooks[name]:
			self.hooks[name].append(cb)

	def run_block(self, name, *args, request=None, **kwargs):
		if name not in self.blocks:
			return ''
		with io.StringIO() as sio:
			for cb in self.blocks[name]:
				if isinstance(cb, TemplateObject):
					sio.write(cb.render(request, argv=args, **kwargs))
				if callable(cb):
					sio.write(cb(*args, **kwargs))
			retv = sio.getvalue()
		return retv

	def run_hook(self, name, *args, request=None, **kwargs):
		if name not in self.hooks:
			return False
		retv = []
		for cb in self.hooks[name]:
			if callable(cb):
				retv.append(cb(*args, **kwargs))
		return retv

class register_block(object):
	def __init__(self, name):
		self.name = name

	def register(self, scanner, name, wrapped):
		hm = scanner.config.registry.getUtility(IHookManager)
		hm.reg_block(self.name, wrapped)

	def __call__(self, wrapped):
		venusian.attach(wrapped, self.register)
		return wrapped

class register_hook(object):
	def __init__(self, name):
		self.name = name

	def register(self, scanner, name, wrapped):
		hm = scanner.config.registry.getUtility(IHookManager)
		hm.reg_hook(self.name, wrapped)

	def __call__(self, wrapped):
		venusian.attach(wrapped, self.register)
		return wrapped

def _reg_hook(cfg, name, cb):
	hm = cfg.registry.getUtility(IHookManager)
	hm.reg_hook(name, cb)

def _reg_block(cfg, name, cb):
	hm = cfg.registry.getUtility(IHookManager)
	hm.reg_block(name, cb)

def _run_hook(request, name, *args, **kwargs):
	hm = request.registry.getUtility(IHookManager)
	return hm.run_hook(name, *args, request=request, **kwargs)

def _run_block(request, name, *args, **kwargs):
	hm = request.registry.getUtility(IHookManager)
	return hm.run_block(name, *args, request=request, **kwargs)

def gen_block(ctx, name, *args, **kwargs):
	req = ctx.get('req')
	kwargs.update(ctx.kwargs)
	hm = req.registry.getUtility(IHookManager)
	return hm.run_block(name, *args, request=req, **kwargs)

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	hm = HookManager()
	config.registry.registerUtility(hm, IHookManager)
	config.add_directive('register_hook', _reg_hook)
	config.add_directive('register_block', _reg_block)
	config.add_request_method(_run_hook, 'run_hook')
	config.add_request_method(_run_block, 'run_block')

