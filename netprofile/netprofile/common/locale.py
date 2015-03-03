#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Localization-related procedures
# © Copyright 2015 Alex 'Unik' Unigovsky
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

