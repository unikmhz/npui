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
from netprofile.db.connection import DBSession
from netprofile_access.models import AccessEntity

from .models import TVSubscription

logger = logging.getLogger(__name__)

_ = TranslationStringFactory('netprofile_tv')


@task_meta(cap='TV_PKG_ASSIGN', title=_('Update TV subscriptions '
                                        'for an access entity'))
@app.task
def update_aent(aeid):
    aeid = int(aeid)
    sess = DBSession()

    # Get a list of all paid service IDs for this entity.
    all_epids = []
    for row in sess.query(TVSubscription.paid_service_id).filter(
            TVSubscription.access_entity_id == aeid):
        if row[0] is not None:
            all_epids.append(row[0])

    # Run paid service accounting, as it might be too fresh otherwise.
    # FIXME: this is MySQL-specific.
    for epid in all_epids:
        sess.execute('CALL ps_execute(:epid, NOW())', {'epid': epid})
    # This is needed because ps_execute itself uses transactions.
    transaction.abort()

    ae = sess.query(AccessEntity).get(aeid)
    if ae is None:
        transaction.abort()
        return

    # Collect all sources used by this entity.
    sources = {}
    for tvcard in ae.tv_cards:
        source = tvcard.source
        if not source.realtime:
            continue
        if source.id not in sources:
            sources[source.id] = source

    # Invoke handlers that do the actual work.
    try:
        for source_id, source in sources.items():
            handler = source.get_handler()
            if not handler:
                continue
            with handler as conn:
                conn.update_access_entity(ae)
    finally:
        transaction.abort()


@task_meta(cap='TV_PKG_ASSIGN', title=_('Update TV subscriptions in bulk'))
@app.task
def update_all():
    transaction.abort()
