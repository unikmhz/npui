#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Access module - reCAPTCHA support
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

from six import PY3
from pyramid.i18n import TranslationStringFactory

if PY3:
    from http.client import HTTPConnection
    from urllib.parse import urlencode
else:
    from httplib import HTTPConnection
    from urllib import urlencode

_ = TranslationStringFactory('netprofile_access')

_ret_codes = {
    'unknown':                  _('Unknown error'),
    'invalid-site-private-key': _('Internal site error'),
    'invalid-request-cookie':   _('reCAPTCHA request error'),
    'incorrect-captcha-sol':    _('Entered text was incorrect'),
    'captcha-timeout':          _('Current CAPTCHA timed out'),
    'recaptcha-not-reachable':  _('reCAPTCHA service is not reachable')
}


class RecaptchaResponse(object):
    def __init__(self, raw):
        if isinstance(raw, bytes):
            raw = raw.decode()
        raw = raw.splitlines()
        self.valid = False
        self.code = 'unknown'
        if len(raw) and raw[0] == 'true':
            self.valid = True
        elif len(raw) > 1:
            self.code = raw[1]

    def text(self):
        if self.code in _ret_codes:
            return _ret_codes[self.code]
        return _('Unknown error')


def verify_recaptcha(private, req):
    ch = req.POST.get('recaptcha_challenge_field', None)
    resp = req.POST.get('recaptcha_response_field', None)
    if not ch or not resp:
        raise ValueError('No reCAPTCHA fields were sent')
    params = urlencode({
        'privatekey': private,
        'remoteip':   req.remote_addr,
        'challenge':  ch,
        'response':   resp
    })
    sock = HTTPConnection('www.google.com')
    sock.request('POST', '/recaptcha/api/verify', params, {
        'Content-type': 'application/x-www-form-urlencoded',
        'Accept':       'text/plain',
        'User-agent':   'NetProfile'
    })
    msg = sock.getresponse()
    data = msg.read()
    sock.close()
    return RecaptchaResponse(data)
