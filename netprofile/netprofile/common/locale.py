#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Localization-related procedures
# © Copyright 2015-2016 Alex 'Unik' Unigovsky
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

import locale

from pyramid.i18n import (
	ITranslationDirectories,
	make_localizer
)

from babel import Locale
from babel.numbers import (
	format_currency,
	format_decimal
)

def sys_localizer(reg):
	cur_locale = reg.settings.get('pyramid.default_locale_name', 'en')
	sys_locale = locale.getlocale()[0]

	if sys_locale:
		new_locale = Locale.negotiate(
			(sys_locale,),
			reg.settings.get('pyramid.available_languages', '').split()
		)
		if new_locale:
			cur_locale = str(new_locale)
	else:
		cur_locale = 'en'

	tdirs = reg.queryUtility(ITranslationDirectories, default=[])
	return make_localizer(cur_locale, tdirs)

def money_format(req, amount, code=None, prefix=None, suffix=None, currency=None):
	if amount is None:
		return ''

	cfg = req.registry.settings
	loc = req.current_locale

	if currency is not None:
		code = currency.code
		prefix = currency.prefix
		suffix = currency.suffix

	if code is None:
		code = cfg.get('netprofile.currency.default')

	if code is None:
		formatted = format_decimal(amount, locale=loc)
	elif code in loc.currencies:
		formatted = format_currency(amount, code, locale=loc)
	else:
		stdloc = req.locales[cfg.get('pyramid.default_locale_name', 'en')]
		if code in stdloc.currencies:
			formatted = format_currency(amount, code, locale=stdloc)
		else:
			formatted = format_decimal(amount, locale=loc)

	ret = []
	if prefix:
		ret.append(prefix)
	ret.append(formatted)
	if suffix:
		ret.append(suffix)
	return '\xa0'.join(ret)

def money_format_long(req, amount, code=None, currency=None):
	if amount is None:
		return ''

	cfg = req.registry.settings
	loc = req.current_locale

	if currency is not None:
		code = currency.code

	if code is None:
		code = cfg.get('netprofile.currency.default')

	if code is not None:
		if code in loc.currencies:
			return format_currency(amount, code, locale=loc, format='0.######## ¤¤¤', currency_digits=False)
		else:
			stdloc = req.locales[cfg.get('pyramid.default_locale_name', 'en')]
			if code in stdloc.currencies:
				return format_currency(amount, code, locale=stdloc, format='0.######## ¤¤¤', currency_digits=False)

	return format_decimal(amount, locale=loc, format='0.########')

