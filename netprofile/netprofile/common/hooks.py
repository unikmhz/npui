#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

	def run_block(self, name, *args, **kwargs):
		if name not in self.blocks:
			return ''
		with io.StringIO() as sio:
			for cb in self.blocks[name]:
				if callable(cb):
					sio.write(cb(*args, **kwargs))
			retv = sio.getvalue()
		return retv

	def run_hook(self, name, *args, **kwargs):
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

def _run_hook(request, name, *args, **kwargs):
	hm = request.registry.getUtility(IHookManager)
	return hm.run_hook(name, *args, **kwargs)

def _run_block(request, name, *args, **kwargs):
	hm = request.registry.getUtility(IHookManager)
	return hm.run_block(name, *args, **kwargs)

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	hm = HookManager()
	config.registry.registerUtility(hm, IHookManager)
	config.add_request_method(_run_hook, 'run_hook')
	config.add_request_method(_run_block, 'run_block')

