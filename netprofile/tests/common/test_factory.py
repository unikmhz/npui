#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Tests for Pyramid root factory
# Copyright © 2017 Alex Unigovsky
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

import unittest
import mock

# Test body begins here

from netprofile.common.factory import RootFactory


class TestRootFactory(unittest.TestCase):
    def test_factory(self):
        req = mock.MagicMock()

        rf = RootFactory(req)
        self.assertEqual(rf.req, req)

        req.acls = 'ACLS'
        self.assertEqual(rf.__acl__, 'ACLS')

        del req.acls
        self.assertEqual(rf.__acl__, ())
