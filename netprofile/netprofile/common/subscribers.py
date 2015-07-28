#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Pyramid event subscribers
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

from pyramid.i18n import (
	TranslationString,
	get_localizer
)

from pyramid.settings import asbool

def add_renderer_globals(event):
	request = event['request']
	if hasattr(request, 'translate'):
		event['_'] = request.translate

def on_new_request(event):
	request = event.request
	mr = request.matched_route
	if mr is None:
		mr = 'netprofile_core'
	else:
		mr = 'netprofile_' + mr.name.split('.')[0]

	def auto_translate(*args, **kwargs):
		if 'domain' not in kwargs:
			kwargs['domain'] = mr
		return get_localizer(request).translate(TranslationString(*args, **kwargs))

	request.translate = auto_translate

def on_response(event):
	settings = event.request.registry.settings
	res = event.response
	# FIXME: add CSP
	res.headerlist.append(('X-Content-Type-Options', 'nosniff'))
	if 'X-Frame-Options' not in res.headers:
		res.headerlist.append(('X-Frame-Options', 'DENY'))
	if asbool(settings.get('netprofile.http.sts.enabled', False)):
		try:
			max_age = int(settings.get('netprofile.http.sts.max_age', 604800))
		except (TypeError, ValueError):
			max_age = 604800
		sts_chunks = [ 'max-age=' + str(max_age) ]
		if asbool(settings.get('netprofile.http.sts.include_subdomains', False)):
			sts_chunks.append('includeSubDomains')
		if asbool(settings.get('netprofile.http.sts.preload', False)):
			sts_chunks.append('preload')
		res.headerlist.append(('Strict-Transport-Security', '; '.join(sts_chunks)))

