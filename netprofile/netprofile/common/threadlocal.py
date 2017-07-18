#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Thread-local storage objects
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

import threading

from netprofile.common import magic as _magic


class TLSMagic(threading.local):
    def __init__(self):
        self.magic = None

    def get(self):
        if self.magic is None:
            m = _magic.open(_magic.MIME | _magic.ERROR)
            if m.load() < 0:
                raise RuntimeError('libMagic load failed')
            self.magic = m
        return self.magic


magic = TLSMagic()
