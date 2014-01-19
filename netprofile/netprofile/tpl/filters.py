#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Filters for Mako templates
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

import datetime, json
from babel.dates import format_date, format_datetime, format_time
from babel.numbers import format_currency
from netprofile.ext.direct import JsonReprEncoder

def jsone(data):
	return json.dumps(data, cls=JsonReprEncoder, indent=3)

def jsone_compact(data):
	return json.dumps(data, cls=JsonReprEncoder, indent=None, separators=(',', ':'))

def date_fmt(ctx, obj, fmt='medium'):
	loc = ctx.get('i18n', None)
	if loc:
		loc = ctx['i18n']
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

def curr_fmt(ctx, obj):
	loc = ctx.get('i18n', None)
	# FIXME: RUB
	if loc:
		return format_currency(obj, '', locale=loc)
	return format_currency(obj, '')

