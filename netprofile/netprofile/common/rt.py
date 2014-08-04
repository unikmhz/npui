#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Async server routines
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

import tornado.httpserver
import tornado.web
import tornado.ioloop

import datetime
import os
import json
import transaction
import redis
import tornadoredis
import tornadoredis.pubsub
import sockjs.tornado

from dateutil.tz import tzlocal
from sqlalchemy.orm.exc import NoResultFound

import netprofile
from netprofile.common.hooks import IHookManager
from netprofile.common.util import make_config_dict
from netprofile.db.connection import DBSession

class RTIndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('rt_index.html', title='NetProfile RT server')

class RTMessageHandler(sockjs.tornado.SockJSConnection):
	def __init__(self, session):
		self.session = session
		self.app = session.server.app
		self.user = None
		self.uid = None
		self.np_session = None

	def _notify_presence(self, event, **kwargs):
		if not self.user:
			return
		sess = self.app.sess
		msg = {
			'type' : event,
			'user' : self.user.login,
			'uid'  : self.uid,
			'msg'  : ''
		}
		msg.update(kwargs)
		sess.r.publish('bcast', json.dumps(msg))

	def on_open(self, req):
		self.user = None
		self.uid = None
		self.np_session = None

	def on_close(self):
		sess = self.app.sess
		sess.sub.unsubscribe('bcast', self)
		if self.user:
			cnt = sess.r.hincrby('rtsess', self.uid, -1)
			if cnt <= 0:
				sess.r.hdel('rtsess', self.uid)
				self._notify_presence('user_leaves')
			sess.sub.unsubscribe('direct.%d' % self.uid, self)
		self.user = None
		self.uid = None
		self.np_session = None

	def on_message(self, msg):
		from netprofile_core import (
			NPSession,
			User
		)
		data = json.loads(msg)
		if not isinstance(data, dict):
			return
		if 'type' not in data:
			return
		print('=========================================================')
		print('MESSAGE')
		print(repr(data))
		print('=========================================================')
		dtype = data['type']

		if dtype == 'auth':
			uid = data.get('uid')
			login = data.get('user')
			sname = data.get('session')
			if (not uid) or (not login) or (not sname):
				return
			db = DBSession()
			npsess = db.query(NPSession).filter(
				NPSession.session_name == sname,
				NPSession.user_id == uid,
				NPSession.login == login
			).one()
			# TODO: check time constraints
			self.np_session = npsess
			self.user = npsess.user
			self.uid = npsess.user.id
			sess = self.app.sess
			cnt = sess.r.hincrby('rtsess', self.uid, 1)
			sess.sub.subscribe((
				'bcast',
				'direct.%d' % self.uid
			), self)
			if cnt == 1:
				self._notify_presence('user_enters')
			self.send(json.dumps({
				'type'  : 'user_list',
				'users' : [int(u) for u in sess.r.hkeys('rtsess')]
			}))
			transaction.commit()
		elif self.user is None:
			return
		elif dtype == 'direct':
			sess = self.app.sess
			msgtype = data.get('msgtype')
			recip = int(data.get('to'))
			data.update({
				'ts'      : datetime.datetime.now().replace(tzinfo=tzlocal()).isoformat(),
				'fromid'  : self.uid,
				'fromstr' : self.user.login
			})
			if msgtype == 'user':
				print('=========================================================')
				print('PUBLISH')
				print(repr(data))
				print('=========================================================')
				sess.r.publish(
					'direct.%d' % recip,
					json.dumps(data)
				)
			transaction.commit()
		else:
			self.app.hm.run_hook('np.rt.message', self, data)
			transaction.commit()

class RTSession(object):
	def __init__(self, reg, r, tr):
		self.reg = reg
		self.r = r
		self.tr = tr
		self.sub = tornadoredis.pubsub.SockJSSubscriber(tr)
		self.routes = [
			(r'/', RTIndexHandler),
		]
		self.sockjs_router = sockjs.tornado.SockJSRouter(RTMessageHandler, '/sock')

	def app(self):
		cfg = make_config_dict(self.reg.settings, 'netprofile.rt.')
		settings = {
			'template_path' : os.path.join(
				os.path.dirname(netprofile.__file__),
				'templates'
			)
		}
		app = tornado.web.Application(
			self.routes + self.sockjs_router.urls,
			**settings
		)
		self.sockjs_router.app = app
		app.sess = self
		app.hm = self.reg.getUtility(IHookManager)
		return app

def run(sess, app):
	cfg = make_config_dict(sess.reg.settings, 'netprofile.rt.')
	sslopts = None
	if cfg.get('ssl'):
		sslopts = {}
		if 'certfile' in cfg:
			sslopts['certfile'] = cfg['certfile']
		if 'keyfile' in cfg:
			sslopts['keyfile'] = cfg['keyfile']
	http_server = tornado.httpserver.HTTPServer(app, ssl_options=sslopts)
	http_server.listen(cfg.get('port'))
#	http_server.bind(cfg.get('port'))
#	http_server.start(0)
	tornado.ioloop.IOLoop.instance().start()

def configure(mmgr, reg):
	cfg = reg.settings
	rconf = make_config_dict(cfg, 'netprofile.rt.redis.')
	trconf = rconf.copy()
	if 'db' in rconf:
		del trconf['db']
		trconf['selected_db'] = rconf['db']
	if 'socket_timeout' in rconf:
		del trconf['socket_timeout']
	if 'charset' in rconf:
		del trconf['charset']
	if 'decode_responses' in rconf:
		del trconf['decode_responses']
	return RTSession(
		reg,
		redis.Redis(**rconf),
		tornadoredis.Client(**trconf)
	)

