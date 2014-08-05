#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Celery application setup
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

import os
import pkg_resources

from pyramid.config import aslist
from pyramid.paster import (
	get_appsettings,
	setup_logging
)

from celery import Celery
from celery.signals import worker_init

from netprofile import setup_config
from netprofile.common.util import make_config_dict

def _parse_ini_settings(settings, celery):
	cfg = make_config_dict(settings, 'celery.')
	newconf = {}

	if 'broker' in cfg:
		newconf['BROKER_URL'] = cfg['broker']
	if 'broker.heartbeat' in cfg:
		newconf['BROKER_HEARTBEAT'] = cfg['broker.heartbeat']
	if 'broker.heartbeat.checkrate' in cfg:
		newconf['BROKER_HEARTBEAT_CHECKRATE'] = cfg['broker.heartbeat.checkrate']
	if 'broker.use_ssl' in cfg:
		newconf['BROKER_USE_SSL'] = cfg['broker.use_ssl']
	if 'broker.pool_limit' in cfg:
		newconf['BROKER_POOL_LIMIT'] = cfg['broker.pool_limit']
	if 'broker.connection.timeout' in cfg:
		newconf['BROKER_CONNECTION_TIMEOUT'] = cfg['broker.connection.timeout']
	if 'broker.connection.retry' in cfg:
		newconf['BROKER_CONNECTION_RETRY'] = cfg['broker.connection.retry']
	if 'broker.connection.max_retries' in cfg:
		newconf['BROKER_CONNECTION_MAX_RETRIES'] = cfg['broker.connection.max_retries']
	if 'broker.login_method' in cfg:
		newconf['BROKER_LOGIN_METHOD'] = cfg['broker.login_method']

	if 'backend' in cfg:
		newconf['CELERY_RESULT_BACKEND'] = cfg['backend']
	if 'task_result_expires' in cfg:
		newconf['CELERY_TASK_RESULT_EXPIRES'] = cfg['task_result_expires']
	if 'task_publish_retry' in cfg:
		newconf['CELERY_TASK_PUBLISH_RETRY'] = cfg['task_publish_retry']
	if 'enable_utc' in cfg:
		newconf['CELERY_ENABLE_UTC'] = cfg['enable_utc']
	if 'timezone' in cfg:
		newconf['CELERY_TIMEZONE'] = cfg['timezone']
	if 'always_eager' in cfg:
		newconf['CELERY_ALWAYS_EAGER'] = cfg['always_eager']
	if 'eager_propagates_exceptions' in cfg:
		newconf['CELERY_EAGER_PROPAGATES_EXCEPTIONS'] = cfg['eager_propagates_exceptions']
	if 'ignore_result' in cfg:
		newconf['CELERY_IGNORE_RESULT'] = cfg['ignore_result']
	if 'message_compression' in cfg:
		newconf['CELERY_MESSAGE_COMPRESSION'] = cfg['message_compression']
	if 'max_cached_results' in cfg:
		newconf['CELERY_MAX_CACHED_RESULTS'] = cfg['max_cached_results']
	if 'chord_propagates' in cfg:
		newconf['CELERY_CHORD_PROPAGATES'] = cfg['chord_propagates']
	if 'track_started' in cfg:
		newconf['CELERY_TRACK_STARTED'] = cfg['track_started']

	if 'accept_content' in cfg:
		newconf['CELERY_ACCEPT_CONTENT'] = aslist(cfg['accept_content'])
	else:
		newconf['CELERY_ACCEPT_CONTENT'] = ('msgpack',)

	if 'task_serializer' in cfg:
		newconf['CELERY_TASK_SERIALIZER'] = cfg['task_serializer']
	else:
		newconf['CELERY_TASK_SERIALIZER'] = 'msgpack'
	if 'result_serializer' in cfg:
		newconf['CELERY_RESULT_SERIALIZER'] = cfg['result_serializer']
	else:
		newconf['CELERY_RESULT_SERIALIZER'] = 'msgpack'

	if 'result_exchange' in cfg:
		newconf['CELERY_RESULT_EXCHANGE'] = cfg['result_exchange']
	if 'result_exchange_type' in cfg:
		newconf['CELERY_RESULT_EXCHANGE_TYPE'] = cfg['result_exchange_type']
	if 'result_persistent' in cfg:
		newconf['CELERY_RESULT_PERSISTENT'] = cfg['result_persistent']
	if 'routes' in cfg:
		newconf['CELERY_ROUTES'] = aslist(cfg['routes'])
	if 'worker_direct' in cfg:
		newconf['CELERY_WORKER_DIRECT'] = cfg['worker_direct']
	if 'create_missing_queues' in cfg:
		newconf['CELERY_CREATE_MISSING_QUEUES'] = cfg['create_missing_queues']

	if 'queue_ha_policy' in cfg:
		qhp = aslist(cfg['queue_ha_policy'])
		if len(qhp) == 1:
			qhp = qhp[0]
		newconf['CELERY_QUEUE_HA_POLICY'] = qhp

	if 'default_queue' in cfg:
		newconf['CELERY_DEFAULT_QUEUE'] = cfg['default_queue']
	if 'default_exchange' in cfg:
		newconf['CELERY_DEFAULT_EXCHANGE'] = cfg['default_exchange']
	if 'default_exchange_type' in cfg:
		newconf['CELERY_DEFAULT_EXCHANGE_TYPE'] = cfg['default_exchange_type']
	if 'default_routing_key' in cfg:
		newconf['CELERY_DEFAULT_ROUTING_KEY'] = cfg['default_routing_key']
	if 'default_delivery_mode' in cfg:
		newconf['CELERY_DEFAULT_DELIVERY_MODE'] = cfg['default_delivery_mode']

	if 'concurrency' in cfg:
		newconf['CELERYD_CONCURRENCY'] = cfg['concurrency']
	if 'prefetch_multiplier' in cfg:
		newconf['CELERYD_PREFETCH_MULTIPLIER'] = cfg['prefetch_multiplier']

	if 'redis_max_connections' in cfg:
		newconf['CELERY_REDIS_MAX_CONNECTIONS'] = cfg['redis_max_connections']

	opts = make_config_dict(cfg, 'broker.transport_options.')
	if len(opts) > 0:
		newconf['BROKER_TRANSPORT_OPTIONS'] = opts

	opts = make_config_dict(cfg, 'task_publish_retry_policy.')
	if len(opts) > 0:
		newconf['CELERY_TASK_PUBLISH_RETRY_POLICY'] = opts

	opts = make_config_dict(cfg, 'result_tables.')
	if len(opts) > 0:
		newconf['CELERY_RESULT_DB_TABLENAMES'] = opts

	opts = make_config_dict(cfg, 'result_options.')
	if len(opts) > 0:
		newconf['CELERY_RESULT_ENGINE_OPTIONS'] = opts

	opts = make_config_dict(cfg, 'cache_options.')
	if len(opts) > 0:
		newconf['CELERY_CACHE_BACKEND_OPTIONS'] = opts

	opts = make_config_dict(cfg, 'mongodb_options.')
	if len(opts) > 0:
		newconf['CELERY_MONGODB_BACKEND_SETTINGS'] = opts

	cass = make_config_dict(cfg, 'cassandra.')
	if 'servers' in cass:
		newconf['CASSANDRA_SERVERS'] = aslist(cass['servers'])
	if 'keyspace' in cass:
		newconf['CASSANDRA_KEYSPACE'] = cass['keyspace']
	if 'column_family' in cass:
		newconf['CASSANDRA_COLUMN_FAMILY'] = cass['column_family']
	if 'read_consistency' in cass:
		newconf['CASSANDRA_READ_CONSISTENCY'] = cass['read_consistency']
	if 'write_consistency' in cass:
		newconf['CASSANDRA_WRITE_CONSISTENCY'] = cass['write_consistency']
	if 'detailed_mode' in cass:
		newconf['CASSANDRA_DETAILED_MODE'] = cass['detailed_mode']
	opts = make_config_dict(cass, 'options.')
	if len(opts) > 0:
		newconf['CASSANDRA_OPTIONS'] = opts

	opts = make_config_dict(cfg, 'queues.')
	if len(opts) > 0:
		newconf['CELERY_QUEUES'] = opts

	if len(newconf) > 0:
		celery.conf.update(newconf)

@worker_init.connect
def _setup(signal, sender):
	ini_file='production.ini'
	if 'NP_INI_FILE' in os.environ:
		ini_file = os.environ['NP_INI_FILE']

	ini_name='netprofile'
	if 'NP_INI_NAME' in os.environ:
		ini_name = os.environ['NP_INI_NAME']

	config_uri = '#'.join((ini_file, ini_name))
	setup_logging(config_uri)
	settings = get_appsettings(config_uri)

	app = sender.app
	app.settings = settings

	cfg = setup_config(settings)
	_parse_ini_settings(settings, app)
#	print(repr(settings))

app = Celery('netprofile')

if __name__ == '__main__':
	app.start()

