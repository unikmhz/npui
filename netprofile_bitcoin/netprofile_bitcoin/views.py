#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile:  Bitcoin module - Views
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
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

#from here, there are several methods added
#that are not in the original lib
#https://github.com/annndrey/bitcoin-python
import re
import bitcoinrpc

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

from netprofile_access.models import AccessEntity

_ = TranslationStringFactory('netprofile_bitcoin')

@view_config(
	route_name='bitcoin.cl.export',
	permission='USAGE',
	renderer='json'
)
def export_key(request):
	cfg = request.registry.settings
	bitcoind_host = cfg.get('netprofile.client.bitcoind.host')
	bitcoind_port = cfg.get('netprofile.client.bitcoind.port')
	bitcoind_login = cfg.get('netprofile.client.bitcoind.login')
	bitcoind_password = cfg.get('netprofile.client.bitcoind.password')
	bitcoind = bitcoinrpc.connect_to_remote(bitcoind_login, bitcoind_password, host=bitcoind_host, port=bitcoind_port)
	resp = {'privkey': None}
	addr = request.GET.get('addr', None)
	if addr:
		resp['privkey'] = bitcoind.dumpprivkey(addr)

	return resp
		
@view_config(
	route_name='bitcoin.cl.create',
	permission='USAGE',
	renderer='json'
)
def create_key(request):
	cfg = request.registry.settings
	bitcoind_host = cfg.get('netprofile.client.bitcoind.host')
	bitcoind_port = cfg.get('netprofile.client.bitcoind.port')
	bitcoind_login = cfg.get('netprofile.client.bitcoind.login')
	bitcoind_password = cfg.get('netprofile.client.bitcoind.password')
	bitcoind = bitcoinrpc.connect_to_remote(bitcoind_login, bitcoind_password, host=bitcoind_host, port=bitcoind_port)

	resp = {'pubkey': None}
	newwallet = None

	if request.GET:
		nextwallet = request.GET.get("newwallet", None)
		if nextwallet:
			newwallet = bitcoind.getnewaddress(nextwallet)
	else:
		privkey = request.POST.get('privkey', None)
		nextwallet = request.POST.get('nextwallet', None)

	
		if privkey:
			newwallet = bitcoind.importprivkey(privkey, nextwallet)

	resp['pubkey'] = newwallet

	return resp


@view_config(
	route_name='bitcoin.cl.wallet',
	permission='USAGE',
	renderer='netprofile_bitcoin:templates/client_bitcoin.mak'
)
def bitcoin_walletss(request):
	loc = get_localizer(request)
	cfg = request.registry.settings
	sess = DBSession()
	errmess = None
	tpldef = {'errmessage':errmess}
	request.run_hook('access.cl.tpldef', tpldef, request)
	access_user = sess.query(AccessEntity).filter_by(nick=str(request.user)).first()
	bitcoind_host = cfg.get('netprofile.client.bitcoind.host')
	bitcoind_port = cfg.get('netprofile.client.bitcoind.port')
	bitcoind_login = cfg.get('netprofile.client.bitcoind.login')
	bitcoind_password = cfg.get('netprofile.client.bitcoind.password')
	userwallets = []
	
	bitcoind = bitcoinrpc.connect_to_remote(bitcoind_login, bitcoind_password, host=bitcoind_host, port=bitcoind_port)

	
	userwallets = [{'wallet':wallet, 'balance':"{0}".format(float(bitcoind.getbalance(wallet))), 'address':bitcoind.getaddressesbyaccount(wallet)} for wallet in bitcoind.listaccounts() if wallet.startswith(access_user.nick)]
	
	if len(userwallets) > 0:
		nextid = max(map(int, re.findall('\d+', ",".join([w['wallet'] for w in userwallets])))) + 1
	else:
		nextid = 0

	nextwallet = "{0}{1}".format(access_user.nick, nextid)

	tpldef.update({'wallets':userwallets, 'nextwallet':nextwallet})

	return tpldef


@register_hook('access.cl.menu')
def _gen_menu(menu, req):
	loc = get_localizer(req)
	menu.append({
		'route' : 'bitcoin.cl.wallet',
		'text'  : loc.translate(_('Bitcoin Wallets'))
	})

