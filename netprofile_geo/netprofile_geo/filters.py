#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.i18n import get_localizer

from netprofile.ext.filters import Filter

class AddressFilter(Filter):
	def get_cfg(self, req):
		loc = get_localizer(req)
		cfg = {
			'xtype'      : 'address',
			'name'       : self.name,
			'fieldLabel' : loc.translate(self.title)
		}
		return cfg

