#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Access module
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

from netprofile.common.modules import ModuleBase
from netprofile.tpl import TemplateObject

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_access')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_access:locale/')
		mmgr.cfg.add_route('access.cl.home', '/', vhost='client')
		mmgr.cfg.add_route('access.cl.login', '/login', vhost='client')
		mmgr.cfg.add_route('access.cl.logout', '/logout', vhost='client')
		mmgr.cfg.add_route('access.cl.upload', '/upload', vhost='client')
		mmgr.cfg.add_route('access.cl.download', '/download/{mode}/{id:\d+}', vhost='client')
		mmgr.cfg.add_route('access.cl.register', '/register', vhost='client')
		mmgr.cfg.add_route('access.cl.regsent', '/regsent', vhost='client')
		mmgr.cfg.add_route('access.cl.activate', '/activate', vhost='client')
		mmgr.cfg.add_route('access.cl.restorepass', '/restorepass', vhost='client')
		mmgr.cfg.add_route('access.cl.restoresent', '/restoresent', vhost='client')
		mmgr.cfg.add_route('access.cl.chpass', '/chpass', vhost='client')
		mmgr.cfg.add_route('access.cl.check.nick', '/check/nick', vhost='client')
		mmgr.cfg.add_route('access.cl.robots', '/robots.txt', vhost='client')
		mmgr.cfg.add_route('access.cl.favicon', '/favicon.ico', vhost='client')
		mmgr.cfg.register_block('stashes.cl.block.info', TemplateObject('netprofile_access:templates/client_block_chrate.mak'))
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('stashes', 'rates', 'ipaddresses')

	@classmethod
	def prepare(cls):
		from netprofile_access import models

	def get_models(self):
		from netprofile_access import models
		return (
			models.AccessEntity,
			models.AccessEntityLink,
			models.AccessEntityLinkType,
			models.PerUserRateModifier
		)

	def get_css(self, request):
		return (
			'netprofile_access:static/css/main.css',
		)

	@property
	def name(self):
		return _('Access')

