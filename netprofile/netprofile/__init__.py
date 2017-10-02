#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Setup and entry points
# Copyright © 2013-2017 Alex Unigovsky
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

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import sys

try:
    import cdecimal
    sys.modules['decimal'] = cdecimal  # pragma: no cover
except ImportError:
    pass

from six import PY3
from babel import Locale
from pyramid.config import Configurator
from pyramid.settings import asbool
from sqlalchemy import engine_from_config

from netprofile.common import cache
from netprofile.common.modules import IModuleManager
from netprofile.common.factory import RootFactory
from netprofile.db.connection import DBSession

from ._version import get_versions

if not PY3:  # pragma: no cover
    # Ugly hack to reset Python 2 default string encoding
    # from ASCII to UTF-8.
    reload(sys)  # noqa: F821
    sys.setdefaultencoding('utf-8')

__version__ = get_versions()['version']
del get_versions

inst_id = 'ru.netprofile'
inst_mm = None


def locale_neg(request):
    avail = request.locales
    loc = request.params.get('__locale')
    if loc is None:
        loc = request.session.get('ui.locale')
    if loc is None and request.accept_language:
        loc = Locale.negotiate(list(request.accept_language),
                               list(request.locales),
                               sep='-')
        if loc:
            loc = str(loc)
    if loc is None:
        loc = request.registry.settings.get('pyramid.default_locale_name',
                                            'en')
    if loc in avail:
        request.session['ui.locale'] = loc
        return loc
    return 'en'


def get_debug(request):
    return request.registry.settings.get('netprofile.debug', False)


def get_locales(request):
    avail = request.registry.settings.get('pyramid.available_languages',
                                          '').split()
    return {loc: Locale.parse(loc) for loc in avail}


def get_current_locale(request):
    if request.locale_name in request.locales:
        return request.locales[request.locale_name]


def get_csrf(request):
    if request.session:
        csrf = request.session.get_csrf_token()
        if isinstance(csrf, bytes):
            csrf = csrf.decode()
        return csrf


class VHostPredicate(object):
    def __init__(self, val, config):
        self.needed = val
        self.current = config.registry.settings.get('netprofile.vhost')

    def text(self):
        return 'vhost = %s' % (self.needed,)

    phash = text

    def __call__(self, context, request):
        if self.needed == 'MAIN':
            return (self.current is None)
        return self.needed == self.current


def setup_config(settings):
    global inst_id

    settings['netprofile.debug'] = asbool(settings.get('netprofile.debug'))
    if 'netprofile.instance_id' in settings:
        inst_id = settings.get('netprofile.instance_id')
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    cache.cache = cache.configure_cache(settings)

    config = Configurator(settings=settings,
                          root_factory=RootFactory,
                          locale_negotiator=locale_neg)
    config.add_route_predicate('vhost', VHostPredicate)
    config.add_view_predicate('vhost', VHostPredicate)
    config.include('netprofile.common.crypto')
    return config


def main(global_config, **settings):
    """
    Pyramid WSGI application for most of NetProfile vhosts.
    """
    config = setup_config(settings)

    config.add_subscriber(
        'netprofile.common.subscribers.add_renderer_globals',
        'pyramid.events.BeforeRender')
    config.add_subscriber(
        'netprofile.common.subscribers.on_new_request',
        'pyramid.events.ContextFound')
    config.add_subscriber(
        'netprofile.common.subscribers.on_response',
        'pyramid.events.NewResponse')
    config.add_request_method(get_locales, str('locales'), reify=True)
    config.add_request_method(get_current_locale,
                              str('current_locale'), reify=True)
    config.add_request_method(get_debug, str('debug_enabled'), reify=True)
    config.add_request_method(get_csrf, str('get_csrf'))

    mmgr = config.registry.getUtility(IModuleManager)
    mmgr.load('core')
    mmgr.load_enabled()

    return config.make_wsgi_app()
