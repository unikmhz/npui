#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Stashes module - Views
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

import math
import datetime as dt
from dateutil.parser import parse as dparse
from dateutil.relativedelta import relativedelta
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.i18n import TranslationStringFactory
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from collections import OrderedDict

from netprofile.common.factory import RootFactory
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from .models import (
    FuturePayment,
    FuturePaymentOrigin,
    Stash,
    StashIO
)

_ = TranslationStringFactory('netprofile_stashes')


@register_hook('core.dpanetabs.entities.Entity')
@register_hook('core.dpanetabs.entities.PhysicalEntity')
@register_hook('core.dpanetabs.entities.LegalEntity')
@register_hook('core.dpanetabs.entities.StructuralEntity')
@register_hook('core.dpanetabs.entities.ExternalEntity')
def _dpane_entity_stashes(tabs, model, req):
    if not req.has_permission('STASHES_LIST'):
        return
    tabs.append({
        'title':             req.localizer.translate(_('Stashes')),
        'iconCls':           'ico-mod-stash',
        'xtype':             'grid_stashes_Stash',
        'stateId':           None,
        'stateful':          False,
        'hideColumns':       ('entity',),
        'extraParamProp':    'entityid',
        'createControllers': 'NetProfile.core.controller.RelatedWizard'
    })


@register_hook('core.dpanetabs.stashes.Stash')
def _dpane_stash_tabs(tabs, model, req):
    loc = req.localizer
    if req.has_permission('STASHES_IO'):
        tabs.append({
            'title':             loc.translate(_('Operations')),
            'iconCls':           'ico-mod-stashio',
            'xtype':             'grid_stashes_StashIO',
            'stateId':           None,
            'stateful':          False,
            'hideColumns':       ('stash',),
            'extraParamProp':    'stashid',
            'createControllers': 'NetProfile.core.controller.RelatedWizard'
        })
    if req.has_permission('FUTURES_LIST'):
        tabs.append({
            'title':             loc.translate(_('Promised Payments')),
            'iconCls':           'ico-mod-stashio',
            'xtype':             'grid_stashes_FuturePayment',
            'stateId':           None,
            'stateful':          False,
            'hideColumns':       ('stash',),
            'extraParamProp':    'stashid',
            'createControllers': 'NetProfile.core.controller.RelatedWizard'
        })


class ClientRootFactory(RootFactory):
    def __getitem__(self, name):
        if not self.req.user:
            raise KeyError('Not logged in')
        try:
            name = int(name, base=10)
            ent = self.req.user.parent
            sess = DBSession()
            try:
                st = sess.query(Stash).filter(
                        Stash.entity == ent,
                        Stash.id == name).one()
                st.__parent__ = self
                st.__name__ = str(name)
                return st
            except NoResultFound:
                raise KeyError('Invalid stash ID')
        except ValueError:
            pass
        raise KeyError('Invalid URL')


@view_config(route_name='stashes.cl.accounts', name='',
             context=ClientRootFactory, permission='USAGE',
             renderer='netprofile_stashes:templates/client_stashes.mak')
@view_config(route_name='stashes.cl.accounts', name='',
             context=Stash, permission='USAGE',
             renderer='netprofile_stashes:templates/client_stashes.mak')
def client_list(ctx, request):
    tpldef = {'stashes': None, 'sname': None, 'extra_tabs': OrderedDict()}
    if isinstance(ctx, Stash):
        tpldef['sname'] = ctx.name
        tpldef['stashes'] = (ctx,)
        tpldef['crumbs'] = [{
            'text': request.localizer.translate(_('My Accounts')),
            'url':  request.route_url('stashes.cl.accounts', traverse=())
        }, {
            'text': ctx.name
        }]
    else:
        tpldef['stashes'] = request.user.parent.stashes
    request.run_hook('access.cl.tpldef', tpldef, request)
    request.run_hook('access.cl.tpldef.accounts.list', tpldef, request)
    return tpldef


@view_config(route_name='stashes.cl.accounts', name='promise',
             context=Stash, request_method='POST', permission='USAGE')
def client_promise(ctx, request):
    loc = request.localizer
    csrf = request.POST.get('csrf', '')
    diff = request.POST.get('diff', '')

    if 'submit' in request.POST:
        sess = DBSession()
        if csrf != request.get_csrf():
            request.session.flash({
                'text': loc.translate(_('Error submitting form')),
                'class': 'danger'
            })
            return HTTPSeeOther(location=request.route_url(
                    'stashes.cl.accounts',
                    traverse=()))
        if ctx.credit > 0:
            request.session.flash({
                'text': loc.translate(
                    _('This account already has active promised payment')),
                'class': 'warning'
            })
            return HTTPSeeOther(location=request.route_url(
                    'stashes.cl.accounts',
                    traverse=()))
        fp = FuturePayment()
        fp.stash = ctx
        fp.entity = request.user.parent
        fp.origin = FuturePaymentOrigin.user
        fp.difference = diff
        sess.add(fp)
        request.session.flash({
            'text': loc.translate(_('Successfully added new promised payment'))
        })
        return HTTPSeeOther(location=request.route_url('stashes.cl.accounts',
                                                       traverse=()))

    request.session.flash({
        'text': loc.translate(_('Error submitting form')),
        'class': 'danger'
    })

    return HTTPSeeOther(location=request.route_url('stashes.cl.accounts',
                                                   traverse=()))


@view_config(route_name='stashes.cl.accounts', name='ops',
             context=ClientRootFactory,
             renderer='netprofile_stashes:templates/client_stats.mak',
             permission='USAGE')
@view_config(route_name='stashes.cl.accounts', name='ops',
             context=Stash,
             renderer='netprofile_stashes:templates/client_stats.mak',
             permission='USAGE')
def client_ops(ctx, request):
    loc = request.localizer
    page = int(request.params.get('page', 1))
    # FIXME: make per_page configurable
    per_page = 30
    ts_from = request.params.get('from')
    ts_to = request.params.get('to')
    ts_now = dt.datetime.now()
    sname = None
    stash_ids = tuple()
    if ts_from:
        try:
            ts_from = dparse(ts_from)
        except ValueError:
            ts_from = None
    else:
        ts_from = None
    if ts_to:
        try:
            ts_to = dparse(ts_to)
        except ValueError:
            ts_to = None
    else:
        ts_to = None
    if ts_from is None:
        ts_from = request.session.get('ops_ts_from')
    if ts_to is None:
        ts_to = request.session.get('ops_ts_to')
    if ts_from is None:
        ts_from = ts_now.replace(day=1, hour=0, minute=0, second=0,
                                 microsecond=0)
    if ts_to is None:
        ts_to = ts_from.replace(hour=23, minute=59, second=59,
                                microsecond=999999) + relativedelta(months=1,
                                                                    days=-1)
    request.session['ops_ts_from'] = ts_from
    request.session['ops_ts_to'] = ts_to
    sess = DBSession()
    ent = request.user.parent
    if isinstance(ctx, Stash):
        stash_ids = (ctx.id,)
        sname = ctx.name
    else:
        stash_ids = [s.id for s in ent.stashes]
    total = sess.query(func.count('*')).select_from(StashIO).filter(
            StashIO.stash_id.in_(stash_ids),
            StashIO.timestamp.between(ts_from, ts_to)).scalar()
    max_page = int(math.ceil(total / per_page))
    if max_page <= 0:
        max_page = 1
    if page <= 0:
        page = 1
    elif page > max_page:
        page = max_page
    ios = sess.query(StashIO).filter(
            StashIO.stash_id.in_(stash_ids),
            StashIO.timestamp.between(ts_from, ts_to)).order_by(
                    StashIO.timestamp.desc())
    if total > per_page:
        ios = ios.offset((page - 1) * per_page).limit(per_page)

    crumbs = [{
        'text': loc.translate(_('My Accounts')),
        'url':  request.route_url('stashes.cl.accounts', traverse=())
    }]
    if sname:
        crumbs.append({
            'text': sname,
            'url':  request.route_url('stashes.cl.accounts',
                                      traverse=(ctx.id,))
        })
    crumbs.append({'text': loc.translate(_('Account Operations'))})
    tpldef = {
        'ts_from': ts_from,
        'ts_to':   ts_to,
        'sname':   sname,
        'page':    page,
        'perpage': per_page,
        'maxpage': max_page,
        'ios':     ios.all(),
        'crumbs':  crumbs
    }

    request.run_hook('access.cl.tpldef', tpldef, request)
    request.run_hook('access.cl.tpldef.accounts.ops', tpldef, request)
    return tpldef


@register_hook('access.cl.menu')
def _gen_menu(menu, req):
    menu.append({
        'route': 'stashes.cl.accounts',
        'text':  _('Accounts')
    })
