#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: XOP module - Views
# Copyright © 2014-2017 Alex Unigovsky
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

from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config, exception_view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPForbidden
from sqlalchemy.orm.exc import NoResultFound

from netprofile.common.factory import RootFactory
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from .models import ExternalOperationProvider
from .exceptions import ExternalOperationError

_ = TranslationStringFactory('netprofile_xop')


@register_hook('core.dpanetabs.stashes.Stash')
def _dpane_stash_futures(tabs, model, req):
    if not req.has_permission('STASHES_IO'):
        return
    tabs.append({
        'title':             req.localizer.translate(_('External Operations')),
        'iconCls':           'ico-mod-externaloperation',
        'xtype':             'grid_xop_ExternalOperation',
        'stateId':           None,
        'stateful':          False,
        'hideColumns':       ('stash',),
        'extraParamProp':    'stashid',
        'createControllers': 'NetProfile.core.controller.RelatedWizard'
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
                        ExternalOperationProvider.enabled.is_(True)).one()
                xopp.__parent__ = self
                xopp.__name__ = xopp.uri
                return xopp
            except NoResultFound:
                raise KeyError('Invalid URI')
        except ValueError:
            pass
        raise KeyError('Invalid URI')


@view_config(route_name='xop.cl.home', name='',
             context=ExternalOperationProvider,
             permission='USAGE')
def xop_request(ctx, request):
    # TODO: add optional redirect-to-site?
    if not ctx.can_access(request):
        raise HTTPForbidden('Access Denied')
    gw = ctx.get_gateway()
    if not gw or not hasattr(gw, 'process_request'):
        raise HTTPForbidden('Access Denied')
    if not callable(gw.process_request):
        raise HTTPForbidden('Access Denied')

    try:
        sess = DBSession()
        xoplist = gw.process_request(request, sess)
    except Exception as e:
        # TODO: cancel and log?
        raise HTTPForbidden('Access Denied')
    for xop in xoplist:
        ctx.check_operation(xop)
        sess.add(xop)

    if hasattr(gw, 'generate_response') and callable(gw.generate_response):
        return gw.generate_response(request, xoplist)

    raise HTTPForbidden('Not Implemented')

@exception_view_config(ExternalOperationError, vhost='xop')
def xop_error(exception, request):
    if exception.xop:
        gw = exception.xop.provider.get_gateway()
        if hasattr(gw, 'generate_error') and callable(gw.generate_error):
            return gw.generate_error(request, exception)
        raise HTTPForbidden('Not Implemented')
    raise HTTPForbidden('Unknown Error')
