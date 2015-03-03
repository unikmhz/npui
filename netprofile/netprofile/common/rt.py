#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Async server routines
# © Copyright 2014-2015 Alex 'Unik' Unigovsky
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
import tornado.gen
import tornado.ioloop

import datetime
import os
import json
import transaction
import redis
import tcelery
import tornadoredis
import tornadoredis.pubsub
import sockjs.tornado

from queue import Queue
from threading import Thread
from functools import partial
from dateutil.tz import tzlocal
from sqlalchemy.orm.exc import NoResultFound
from pyramid.decorator import reify

import netprofile
from netprofile.common.hooks import IHookManager
from netprofile.common.util import make_config_dict
from netprofile.db.connection import DBSession
from netprofile.celery import app as celery_app
from netprofile.celery import setup_celery

class WorkerThread(Thread):
	def __init__(self, queue):
		super(WorkerThread, self).__init__()
		self.queue = queue
		self.daemon = True
		self.start()

	def run(self):
		while True:
			func, args, kwargs, callback = self.queue.get()
			try:
				result = func(*args, **kwargs)
				if callback is not None:
					tornado.ioloop.IOLoop.current().add_callback(partial(callback, result))
			except Exception as e:
				print(e)
			self.queue.task_done()

class ThreadPool(object):
	def __init__(self, num_threads):
		self.queue = Queue()
		for idx in range(num_threads):
			WorkerThread(self.queue)

	def add_task(self, func, args=(), kwargs={}, callback=None):
		self.queue.put((func, args, kwargs, callback))

	def wait_completion(self):
		self.queue.join()

class RTIndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('rt_index.html', title='NetProfile RT server')

class RTMessageHandler(sockjs.tornado.SockJSConnection):
	def __init__(self, session):
		self.session = session
		self.app = session.server.app
		self.user = None
		self.np_session = None
		self.privileges = ()

	@property
	def thread_pool(self):
		if not hasattr(self.app, 'thread_pool'):
			self.app.thread_pool = ThreadPool(8) # FIXME: make configurable
		return self.app.thread_pool

	def _notify_presence(self, event, **kwargs):
		if not self.user:
			return
		sess = self.app.sess
		msg = {
			'type' : event,
			'user' : self.user.login,
			'uid'  : self.user.id,
			'msg'  : ''
		}
		msg.update(kwargs)
		sess.r.publish('bcast', json.dumps(msg))

	def _get_db_session(self, uid, login, sname):
		from netprofile_core import (
			NPSession,
			User
		)
		db = DBSession()
		try:
			npsess = db.query(NPSession).filter(
				NPSession.session_name == sname,
				NPSession.user_id == uid,
				NPSession.login == login
			).one()
		except NoResultFound:
			transaction.abort()
			return None
		npuser = npsess.user
		privs = npuser.flat_privileges
		db.expunge(npuser)
		db.expunge(npsess)
		# TODO: compute next session timeout check
		transaction.abort()
		return (npsess, npuser, privs)

	def on_open(self, req):
		self.user = None
		self.np_session = None
		self.privileges = ()

	def on_close(self):
		sess = self.app.sess
		sess.sub.unsubscribe('bcast', self)
		if self.user:
			cnt = sess.r.hincrby('rtsess', self.user.id, -1)
			if cnt <= 0:
				sess.r.hdel('rtsess', self.user.id)
				self._notify_presence('user_leaves')
			sess.sub.unsubscribe('direct.%d' % self.user.id, self)
		self.user = None
		self.np_session = None
		self.privileges = ()

	@tornado.gen.engine
	def on_message(self, msg):
		data = json.loads(msg)
		if not isinstance(data, dict):
			return
		if 'type' not in data:
			return
		dtype = data['type']

		if dtype == 'auth':
			uid = data.get('uid')
			login = data.get('user')
			sname = data.get('session')
			if (not uid) or (not login) or (not sname):
				return # FIXME: report error

			dbres = yield tornado.gen.Task(
				self.thread_pool.add_task,
				self._get_db_session,
				(uid, login, sname)
			)
			if dbres is None:
				return # FIXME: report error

			self.np_session = dbres[0]
			self.user = dbres[1]
			self.privileges = dbres[2]

			sess = self.app.sess
			cnt = sess.r.hincrby('rtsess', self.user.id, 1)
			sess.sub.subscribe((
				'bcast',
				'direct.%d' % self.user.id
			), self)
			if cnt == 1:
				self._notify_presence('user_enters')
			self.send(json.dumps({
				'type'  : 'user_list',
				'users' : [int(u) for u in sess.r.hkeys('rtsess')]
			}))
		elif self.user is None:
			return
		elif dtype == 'direct':
			sess = self.app.sess
			msgtype = data.get('msgtype')
			recip = int(data.get('to'))
			data.update({
				'ts'      : datetime.datetime.now().replace(tzinfo=tzlocal()).isoformat(),
				'fromid'  : self.user.id,
				'fromstr' : self.user.login
			})
			if msgtype == 'user':
				sess.r.publish(
					'direct.%d' % recip,
					json.dumps(data)
				)
		elif dtype == 'task':
			task_name = data.get('tname')
			task_args = data.get('args', [])
			task_kwargs = data.get('kwargs', {})

			if task_name not in celery_app.tasks:
				self.send(json.dumps({
					'ts'    : datetime.datetime.now().replace(tzinfo=tzlocal()).isoformat(),
					'type'  : 'task_error',
					'tname' : task_name,
					'errno' : 404,
					'value' : 'No task found'
				}))
				return
			task = celery_app.tasks[task_name]
			task_cap = getattr(task, '__cap__', None)
			if task_cap:
				if (not self.privileges) or (not self.privileges.get(task_cap, False)):
					self.send(json.dumps({
						'ts'    : datetime.datetime.now().replace(tzinfo=tzlocal()).isoformat(),
						'type'  : 'task_error',
						'tname' : task_name,
						'errno' : 403,
						'value' : 'Access denied'
					}))
					return

			resp = yield tornado.gen.Task(
				task.apply_async,
				args=task_args,
				kwargs=task_kwargs
			)

			# TODO: proper error handling w/ passing debug stacktraces to client
			if resp.traceback:
				print(resp.traceback)

			rdata = {
				'ts'    : datetime.datetime.now().replace(tzinfo=tzlocal()).isoformat(),
				'type'  : 'task_result',
				'tname' : task_name,
				'tid'   : resp.task_id,
				'value' : resp.result
			}
			self.send(json.dumps(rdata))
		else:
			self.app.hm.run_hook('np.rt.message', self, data)

class RTSession(object):
	def __init__(self, reg, r, tr):
		self.reg = reg
		self.r_conf = r
		self.tr_conf = tr
		self.routes = [
			(r'/', RTIndexHandler),
		]

	def app(self):
		cfg = make_config_dict(self.reg.settings, 'netprofile.rt.')
		settings = {
			'template_path' : os.path.join(
				os.path.dirname(netprofile.__file__),
				'templates'
			)
		}
		app = tornado.web.Application(self.routes, **settings)
		app.sess = self
		app.hm = self.reg.getUtility(IHookManager)
		return app

	@reify
	def r(self):
		return redis.Redis(**self.r_conf)

	@reify
	def tr(self):
		return tornadoredis.Client(**self.tr_conf)

	@reify
	def sub(self):
		return tornadoredis.pubsub.SockJSSubscriber(self.tr)

	@reify
	def sockjs_router(self):
		return sockjs.tornado.SockJSRouter(RTMessageHandler, '/sock')

	def add_sockjs_routes(self, app):
		app.add_handlers('.*$', self.sockjs_router.urls)
		self.sockjs_router.app = app

def run(sess):
	cfg = make_config_dict(sess.reg.settings, 'netprofile.rt.')
	sslopts = None
	if cfg.get('ssl'):
		sslopts = {}
		if 'certfile' in cfg:
			sslopts['certfile'] = cfg['certfile']
		if 'keyfile' in cfg:
			sslopts['keyfile'] = cfg['keyfile']
	app = sess.app()
	http_server = tornado.httpserver.HTTPServer(app, ssl_options=sslopts)
	http_server.bind(int(cfg.get('port', 8808)))
	http_server.start(int(cfg.get('processes', 0)))
	sess.add_sockjs_routes(app)
	iol = tornado.ioloop.IOLoop.current()
	setup_celery(sess.reg)
	tcelery.setup_nonblocking_producer(celery_app, io_loop=iol)
	iol.start()

	return 0

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
	return RTSession(reg, rconf, trconf)

