#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Pyramid event subscribers
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

from pyramid.i18n import TranslationString
from pyramid.settings import asbool

_CACHED_CSP_HEADER = None


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
        return request.localizer.translate(TranslationString(*args, **kwargs))

    request.translate = auto_translate


def on_response(event):
    global _CACHED_CSP_HEADER

    req = event.request
    res = event.response
    settings = req.registry.settings
    vhost = settings.get('netprofile.vhost')

    if vhost is None and not req.path_info.startswith('/_debug_toolbar'):
        if _CACHED_CSP_HEADER is None:
            rt_ssl = asbool(settings.get('netprofile.rt.ssl', False))
            rt_host = settings.get('netprofile.rt.host')
            rt_port = int(settings.get('netprofile.rt.port',
                                       443 if rt_ssl else 80))

            script_src = ["'self'", "'unsafe-eval'"]
            style_src = ["'self'", "'unsafe-inline'"]
            connect_src = ["'self'"]
            font_src = ["'self'"]
            img_src = ["'self'"]
            frame_src = ["'self'"]

            if rt_host:
                rt_url = '%s://%s:%d' % ('https' if rt_ssl else 'http',
                                         rt_host,
                                         rt_port)
                rt_ws_url = '%s://%s:%d' % ('wss' if rt_ssl else 'ws',
                                            rt_host,
                                            rt_port)
                connect_src.extend((rt_url, rt_ws_url))

            # TODO: add staticURL to CSP

            _CACHED_CSP_HEADER = (
                'default-src \'none\'; '
                'script-src %s; '
                'style-src %s; '
                'connect-src %s; '
                'font-src %s; '
                'img-src %s; '
                'frame-src %s;') % (
                    ' '.join(script_src),
                    ' '.join(style_src),
                    ' '.join(connect_src),
                    ' '.join(font_src),
                    ' '.join(img_src),
                    ' '.join(frame_src))

        res.headerlist.append((
            'Content-Security-Policy',
            _CACHED_CSP_HEADER
        ))

    res.headerlist.extend(((
        'X-Content-Type-Options',
        'nosniff'
    ), (
        'X-XSS-Protection',
        '1; mode=block'
    ), (
        'Referrer-Policy',
        'no-referrer'
    )))
    if 'X-Frame-Options' not in res.headers:
        res.headerlist.append(('X-Frame-Options', 'DENY'))
    if asbool(settings.get('netprofile.http.sts.enabled', False)):
        try:
            max_age = int(settings.get('netprofile.http.sts.max_age', 604800))
        except (TypeError, ValueError):
            max_age = 604800
        sts_chunks = ['max-age=' + str(max_age)]
        if asbool(settings.get('netprofile.http.sts.include_subdomains',
                               False)):
            sts_chunks.append('includeSubDomains')
        if asbool(settings.get('netprofile.http.sts.preload', False)):
            sts_chunks.append('preload')
        res.headerlist.append(('Strict-Transport-Security',
                               '; '.join(sts_chunks)))
