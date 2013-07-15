#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from sqlalchemy.orm import (
	scoped_session,
	sessionmaker,
	attributes
)
from sqlalchemy.orm.session import make_transient
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import event

class Versioned(object):
	def new_version(self, sess):
		make_transient(self)
		self.id = None

def _cb_before_flush(sess, flush_ctx, instances):
	versioned_inst = []
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

DBSession = scoped_session(sessionmaker(
	extension=ZopeTransactionExtension()
))
Base = declarative_base()

event.listen(DBSession, 'before_flush', _cb_before_flush)

