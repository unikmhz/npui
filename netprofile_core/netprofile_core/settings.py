#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from sqlalchemy import event
from sqlalchemy.orm.exc import NoResultFound
from netprofile.common.cache import (
	cache,
	NO_VALUE
)
from netprofile.db.connection import DBSession

from .models import GlobalSetting

@cache.cache_on_arguments()
def global_setting(name):
	sess = DBSession()
	try:
		gs = sess.query(GlobalSetting).filter(GlobalSetting.name == name).one()
	except NoResultFound:
		return None
	if gs.value is None:
		return None
	return gs.python_value

def _set_gs(mapper, conn, tgt):
	if tgt.name:
		global_setting.set(tgt.python_value, tgt.name)

def _del_gs(mapper, conn, tgt):
	if tgt.name:
		global_setting.invalidate(tgt.name)

event.listen(GlobalSetting, 'after_delete', _del_gs)
event.listen(GlobalSetting, 'after_insert', _set_gs)
event.listen(GlobalSetting, 'after_update', _set_gs)

