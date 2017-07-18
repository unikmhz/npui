#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Database connections
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

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    attributes
)
from sqlalchemy.schema import MetaData
from sqlalchemy.orm.session import make_transient
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import (
    Sequence,
    event
)


class Versioned(object):
    def new_version(self, sess):
        make_transient(self)
        self.id = None


def _cb_after_create(table, conn, **kwargs):
    for col in table.columns.values():
        if isinstance(col.default, Sequence):
            if (conn.dialect.name == 'mysql') and col.default.start:
                conn.execute('ALTER TABLE %s AUTO_INCREMENT = %d' % (
                    table.name,
                    col.default.start))


def _cb_instrument_class(mapper, cls):
    if mapper.local_table is not None:
        event.listen(mapper.local_table, 'after_create', _cb_after_create)


def _cb_before_flush(sess, flush_ctx, instances):
    for obj in sess.dirty:
        if not isinstance(obj, Versioned):
            continue
        if not sess.is_modified(obj, passive=True, include_collections=False):
            continue
        if not attributes.instance_state(obj).has_identity:
            continue

        old_id = obj.id
        oldv = getattr(obj, 'old_version', None)
        obj.new_version(sess)
        sess.add(obj)
        if oldv and callable(oldv) and old_id:
            oldv(sess, old_id)


_db_naming = {
    'fk': '%(table_name)s_fk_%(column_0_name)s',  # foreign key
    'pk': '%(table_name)s_pk',                    # primary key
    'ix': '%(table_name)s_i_%(column_0_name)s',   # index
    'ck': '%(table_name)s_c_%(column_0_name)s',   # check constraint
    'uq': '%(table_name)s_u_%(column_0_name)s',   # unique constraint
}

DBMeta = MetaData(naming_convention=_db_naming)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base(metadata=DBMeta)

event.listen(Base, 'instrument_class', _cb_instrument_class, propagate=True)
event.listen(DBSession, 'before_flush', _cb_before_flush)
