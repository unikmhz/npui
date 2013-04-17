#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.i18n import (
	TranslationString,
	get_localizer
)

def add_renderer_globals(event):
	request = event['request']
	event['_'] = request.translate

def on_new_request(event):
	request = event.request
	mr = request.matched_route
	if mr is None:
		mr = 'netprofile_core'
	else:
		mr = 'netprofile_' + mr.name.split('.')[0]

	def auto_translate(*args, **kwargs):
		kwargs['domain'] = mr
		return get_localizer(request).translate(TranslationString(*args, **kwargs))

	request.translate = auto_translate

#	request.response.headerlist.append((
#		'Content-Security-Policy',
#		'default-src \'self\'; script-src \'self\' \'unsafe-eval\''
#	))

