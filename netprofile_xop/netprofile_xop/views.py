#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: XOP module - Views
# © Copyright 2014 Alex 'Unik' Unigovsky
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

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

import math
import datetime as dt
from dateutil.parser import parse as dparse
from dateutil.relativedelta import relativedelta

from pyramid.view import view_config
from pyramid.httpexceptions import (
	HTTPForbidden,
	HTTPSeeOther
)
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from netprofile.common.factory import RootFactory
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from .models import (
	ExternalOperation,
	ExternalOperationProvider
)

_ = TranslationStringFactory('netprofile_xop')

@register_hook('core.dpanetabs.stashes.Stash')
def _dpane_stash_futures(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('External Operations')),
		'iconCls'           : 'ico-mod-stashio',
		'xtype'             : 'grid_stashes_ExternalOperation',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('stash',),
		'extraParamProp'    : 'stashid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

class ClientRootFactory(RootFactory):
	def __getitem__(self, uri):
		if not self.req.user:
			raise KeyError('Not logged in')
		try:
			sess = DBSession()
			try:
				xopp = sess.query(ExternalOperationProvider).filter(
					ExternalOperationProvider.uri == uri,
					ExternalOperationProvider.enabled == True
				).one()
				xopp.__parent__ = self
				xopp.__name__ = xopp.sname #???
				return xopp
			except NoResultFound:
				raise KeyError('Invalid URI')
		except ValueError:
			pass
		raise KeyError('Invalid URI')

@view_config(
	route_name='xop.cl.home',
	name='',
	context=ExternalOperationProvider,
	permission='USAGE',
	renderer='netprofile_xop:templates/xop.mak'
)
def xop_magic(ctx, request):
	loc = get_localizer(request)

	cls = ctx.gwclass

	tpldef['cls'] = cls
	#return cls(request)
	return tpldef

