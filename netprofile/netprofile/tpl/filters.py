#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Filters for Mako templates
# © Copyright 2013-2016 Alex 'Unik' Unigovsky
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

import datetime, json
from babel.dates import (
	format_date,
	format_datetime,
	format_time,
	get_date_format,
	get_datetime_format,
	get_time_format
)
from babel.numbers import (
	format_currency,
	format_decimal
)
from netprofile.ext.direct import JsonReprEncoder

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile')

def jsone(data):
	return json.dumps(data, cls=JsonReprEncoder, indent=3)

def jsone_compact(data):
	return json.dumps(data, cls=JsonReprEncoder, indent=None, separators=(',', ':'))

def date_fmt(ctx, obj, fmt='medium'):
	loc = ctx.get('i18n', None)
	if loc:
		if isinstance(obj, datetime.datetime):
			return format_datetime(obj, fmt, locale=loc)
		if isinstance(obj, datetime.time):
			return format_time(obj, fmt, locale=loc)
		if isinstance(obj, datetime.date):
			return format_date(obj, fmt, locale=loc)
	return str(obj)

def date_fmt_short(ctx, obj):
	return date_fmt(ctx, obj, 'short')

def date_fmt_long(ctx, obj):
	return date_fmt(ctx, obj, 'long')

def date_fmt_full(ctx, obj):
	return date_fmt(ctx, obj, 'full')

def datetime_fmt_tpl(ctx, fmt='medium'):
	loc = ctx.get('i18n', None)
	if loc:
		return get_datetime_format(fmt, loc).format(
			get_time_format(fmt, loc).pattern,
			get_date_format(fmt, loc).pattern
		)
	return get_datetime_format(fmt).format(
		get_time_format(fmt).pattern,
		get_date_format(fmt).pattern
	)

def bytes_fmt(ctx, obj):
	req = ctx.get('req', None)
	i18n = ctx.get('i18n', None)
	loc = None
	if req:
		loc = get_localizer(req)
	suffix = _('B')

	if obj > 1073741824:
		obj = obj / 1073741824
		suffix = _('GiB')
	elif obj > 1048576:
		obj = obj / 1048576
		suffix = _('MiB')
	elif obj > 1024:
		obj = obj / 1024
		suffix = _('KiB')
	if loc:
		suffix = loc.translate(suffix)
	if i18n:
		obj = format_decimal(obj, '#,##0.###;-#', i18n)
	else:
		obj = format_decimal(obj, '#,##0.###;-#')
	return '%s %s' % (obj, suffix)

