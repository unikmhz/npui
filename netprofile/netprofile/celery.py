#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Celery application setup
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

import os

from pyramid.config import aslist
from pyramid.paster import (
    get_appsettings,
    setup_logging
)
from celery import (
    Celery,
    signals
)
from celery.loaders.base import BaseLoader
from kombu import (
    Exchange,
    Queue
)
from kombu.common import Broadcast
from sqlalchemy import (
    engine_from_config,
    event,
    pool
)

from netprofile import setup_config
from netprofile.common.modules import IModuleManager
from netprofile.common.util import (
    as_dict,
    make_config_dict
)
from netprofile.db.clauses import (
    SetVariable,
    SetVariables
)
from netprofile.db.connection import DBSession

_default_queues = (
    Queue('celery', Exchange('celery'), routing_key='celery'),
    Broadcast('broadcast')
)


def _parse_ini_settings(reg):
    settings = reg.settings
    cfg = make_config_dict(settings, 'celery.')

    if 'accept_content' in cfg:
        cfg['accept_content'] = aslist(cfg['accept_content'])
    else:
        cfg['accept_content'] = ('msgpack',)

    if 'task_serializer' not in cfg:
        cfg['task_serializer'] = 'msgpack'
    if 'result_serializer' not in cfg:
        cfg['result_serializer'] = 'msgpack'
    if 'event_serializer' not in cfg:
        cfg['event_serializer'] = 'msgpack'

    if 'task_routes' in cfg:
        cfg['task_routes'] = aslist(cfg['task_routes'])

    if 'task_queue_ha_policy' in cfg:
        qhp = aslist(cfg['task_queue_ha_policy'])
        if len(qhp) == 1:
            qhp = qhp[0]
        cfg['task_queue_ha_policy'] = qhp

    if 'beat_scheduler' not in cfg:
        # FIXME: strip scheduler parts out of 'core' module
        cfg['beat_scheduler'] = 'netprofile_core.celery:Scheduler'

    # FIXME: complex python values!
    opts = make_config_dict(cfg, 'beat_schedule.')
    if len(opts) > 0:
        cfg['beat_schedule'] = as_dict(opts)

    opts = make_config_dict(cfg, 'broker_transport_options.')
    if len(opts) > 0:
        cfg['broker_transport_options'] = opts

    opts = make_config_dict(cfg, 'task_publish_retry_policy.')
    if len(opts) > 0:
        cfg['task_publish_retry_policy'] = opts

    opts = make_config_dict(cfg, 'database_db_names.')
    if len(opts) > 0:
        cfg['database_db_names'] = opts

    opts = make_config_dict(cfg, 'database_engine_options.')
    if len(opts) > 0:
        cfg['database_engine_options'] = opts

    opts = make_config_dict(cfg, 'cache_backend_options.')
    if len(opts) > 0:
        cfg['cache_backend_options'] = opts

    opts = make_config_dict(cfg, 'mongodb_backend_settings.')
    if len(opts) > 0:
        cfg['mongodb_backend_settings'] = opts

    if 'cassandra_servers' in cfg:
        cfg['cassandra_servers'] = aslist(cfg['cassandra_servers'])

    opts = make_config_dict(cfg, 'cassandra_auth_kwargs.')
    if len(opts) > 0:
        cfg['cassandra_auth_kwargs'] = as_dict(opts)

    opts = make_config_dict(cfg, 'task_queues.')
    if len(opts) > 0:
        cfg['task_queues'] = opts
    else:
        cfg['task_queues'] = _default_queues

    mm = reg.getUtility(IModuleManager)

    opts = []
    if 'imports' in cfg:
        opts = aslist(cfg['imports'])
    for imp in mm.get_task_imports():
        opts.append(imp)
    cfg['imports'] = opts

    opts = []
    if 'include' in cfg:
        opts = aslist(cfg['include'])
    # FIXME: hook module include here (?)
    cfg['include'] = opts

    return cfg


class AppLoader(BaseLoader):
    def read_configuration(self, env='CELERY_CONFIG_MODULE'):
        ini_file = 'production.ini'
        if 'NP_INI_FILE' in os.environ:
            ini_file = os.environ['NP_INI_FILE']

        ini_name = 'netprofile'
        if 'NP_INI_NAME' in os.environ:
            ini_name = os.environ['NP_INI_NAME']

        config_uri = '#'.join((ini_file, ini_name))
        setup_logging(config_uri)
        settings = get_appsettings(config_uri)

        cfg = setup_config(settings)
        cfg.commit()

        mmgr = cfg.registry.getUtility(IModuleManager)
        mmgr.load('core')
        mmgr.load_enabled()

        self.app.config = cfg
        self.app.settings = settings
        self.app.mmgr = mmgr

        return _parse_ini_settings(cfg.registry)


app = Celery('netprofile')


def task_meta(**kwargs):
    def _app_task_wrapper(wrapped):
        if 'title' in kwargs:
            wrapped.__title__ = kwargs['title']
        if 'cap' in kwargs:
            wrapped.__cap__ = kwargs['cap']
        return wrapped

    return _app_task_wrapper


def _worker_setup(*args, **kwargs):
    DBSession.remove()
    engine = engine_from_config(app.settings,
                                prefix='sqlalchemy.',
                                poolclass=pool.NullPool)
    DBSession.configure(bind=engine)

    def _after_begin(sess, trans, conn):
        try:
            sess.execute(SetVariables(
                accessuid=0,
                accessgid=0,
                accesslogin='[TASK]'))
        except NotImplementedError:
            sess.execute(SetVariable('accessuid', 0))
            sess.execute(SetVariable('accessgid', 0))
            sess.execute(SetVariable('accesslogin', '[TASK]'))

    event.listen(DBSession, 'after_begin', _after_begin)


signals.worker_process_init.connect(_worker_setup)
signals.beat_init.connect(_worker_setup)


def setup_celery(reg):
    celery_conf = _parse_ini_settings(reg)
    app.config_from_object(celery_conf)


def includeme(config):
    """
    For inclusion by Pyramid.
    """
    setup_celery(config.registry)


if __name__ == '__main__':
    app.start()
