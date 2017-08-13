#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: TV subscription module - Tasks
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

import logging
import transaction
from pyramid.i18n import TranslationStringFactory

from netprofile.celery import (
    app,
    task_meta
)

logger = logging.getLogger(__name__)

_ = TranslationStringFactory('netprofile_tv')


@task_meta(cap='TV_PKG_ASSIGN', title=_('Update TV subscriptions for a user'))
@app.task
def update_user(user_id):
    transaction.abort()
    return


@task_meta(cap='TV_PKG_ASSIGN', title=_('Update TV subscriptions in bulk'))
@app.task
def update_all():
    transaction.abort()
    return
