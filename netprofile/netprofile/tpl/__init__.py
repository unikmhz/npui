#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.renderers import render

class TemplateObject(object):
	def __init__(self, path, **kwargs):
		self.path = path
		self.args = kwargs

	def render(self, req):
		return render(self.path, self.args, request=req)

