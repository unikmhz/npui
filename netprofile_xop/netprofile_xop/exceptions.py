#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: XOP module - Exceptions
# Copyright © 2017 Nikita Andriyanov
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


class ExternalOperationError(RuntimeError):
    def __init__(self, error, xop=None):
        self.error = error
        self.xop = xop


class ExternalOperationProviderError(RuntimeError):
    def __init__(self, error, provider=None):
        self.error = error
        self.provider = provider
