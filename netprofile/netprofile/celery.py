#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Celery application setup
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

import os
import pkg_resources

from pyramid.config import aslist
from pyramid.paster import (
	get_appsettings,
	setup_logging
)

from celery import Celery
from celery.signals import celeryd_init
from kombu import (
	Exchange,
	Queue
)
from kombu.common import Broadcast

from netprofile import setup_config
from netprofile.common.modules import IModuleManager
from netprofile.common.util import (
	as_dict,
	make_config_dict
)

_default_queues = (
	Queue('celery', Exchange('celery'), routing_key='celery'),
	Broadcast('broadcast')
)

def _parse_ini_settings(reg, celery):
	settings = reg.settings
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
	if 'store_errors_even_if_ignored' in cfg:
		newconf['CELERY_STORE_ERRORS_EVEN_IF_IGNORED'] = cfg['store_errors_even_if_ignored']
	if 'message_compression' in cfg:
		newconf['CELERY_MESSAGE_COMPRESSION'] = cfg['message_compression']
	if 'max_cached_results' in cfg:
		newconf['CELERY_MAX_CACHED_RESULTS'] = cfg['max_cached_results']
	if 'chord_propagates' in cfg:
		newconf['CELERY_CHORD_PROPAGATES'] = cfg['chord_propagates']
	if 'track_started' in cfg:
		newconf['CELERY_TRACK_STARTED'] = cfg['track_started']
	if 'default_rate_limit' in cfg:
		newconf['CELERY_DEFAULT_RATE_LIMIT'] = cfg['default_rate_limit']
	if 'disable_rate_limits' in cfg:
		newconf['CELERY_DISABLE_RATE_LIMITS'] = cfg['disable_rate_limits']
	if 'acks_late' in cfg:
		newconf['CELERY_ACKS_LATE'] = cfg['acks_late']

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
	if 'event_serializer' in cfg:
		newconf['CELERY_EVENT_SERIALIZER'] = cfg['event_serializer']
	else:
		newconf['CELERY_EVENT_SERIALIZER'] = 'msgpack'

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
	if 'enable_remote_control' in cfg:
		newconf['CELERY_ENABLE_REMOTE_CONTROL'] = cfg['enable_remote_control']

	if 'send_task_error_emails' in cfg:
		newconf['CELERY_SEND_TASK_ERROR_EMAILS'] = cfg['send_task_error_emails']
#	if 'admins' in cfg:
#		FIXME: list of tuples
	if 'server_email' in cfg:
		newconf['SERVER_EMAIL'] = cfg['server_email']
	if 'email_host' in cfg:
		newconf['EMAIL_HOST'] = cfg['email_host']
	if 'email_host_user' in cfg:
		newconf['EMAIL_HOST_USER'] = cfg['email_host_user']
	if 'email_host_password' in cfg:
		newconf['EMAIL_HOST_PASSWORD'] = cfg['email_host_password']
	if 'email_port' in cfg:
		newconf['EMAIL_PORT'] = cfg['email_port']
	if 'email_use_ssl' in cfg:
		newconf['EMAIL_USE_SSL'] = cfg['email_use_ssl']
	if 'email_use_tls' in cfg:
		newconf['EMAIL_USE_TLS'] = cfg['email_use_tls']
	if 'email_timeout' in cfg:
		newconf['EMAIL_TIMEOUT'] = cfg['email_timeout']

	if 'send_events' in cfg:
		newconf['CELERY_SEND_EVENTS'] = cfg['send_events']
	if 'send_task_sent_event' in cfg:
		newconf['CELERY_SEND_TASK_SENT_EVENT'] = cfg['send_task_sent_event']
	if 'event_queue_ttl' in cfg:
		newconf['CELERY_EVENT_QUEUE_TTL'] = cfg['event_queue_ttl']
	if 'event_queue_expires' in cfg:
		newconf['CELERY_EVENT_QUEUE_EXPIRES'] = cfg['event_queue_expires']
	if 'redirect_stdouts' in cfg:
		newconf['CELERY_REDIRECT_STDOUTS'] = cfg['redirect_stdouts']
	if 'redirect_stdouts_level' in cfg:
		newconf['CELERY_REDIRECT_STDOUTS_LEVEL'] = cfg['redirect_stdouts_level']

	if 'queue_ha_policy' in cfg:
		qhp = aslist(cfg['queue_ha_policy'])
		if len(qhp) == 1:
			qhp = qhp[0]
		newconf['CELERY_QUEUE_HA_POLICY'] = qhp

	if 'security_key' in cfg:
		newconf['CELERY_SECURITY_KEY'] = cfg['security_key']
	if 'security_certificate' in cfg:
		newconf['CELERY_SECURITY_CERTIFICATE'] = cfg['security_certificate']
	if 'security_cert_store' in cfg:
		newconf['CELERY_SECURITY_CERT_STORE'] = cfg['security_cert_store']

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
	if 'force_execv' in cfg:
		newconf['CELERYD_FORCE_EXECV'] = cfg['force_execv']
	if 'worker_lost_wait' in cfg:
		newconf['CELERYD_WORKER_LOST_WAIT'] = cfg['worker_lost_wait']
	if 'max_tasks_per_child' in cfg:
		newconf['CELERYD_MAX_TASKS_PER_CHILD'] = cfg['max_tasks_per_child']
	if 'task_time_limit' in cfg:
		newconf['CELERYD_TASK_TIME_LIMIT'] = cfg['task_time_limit']
	if 'task_soft_time_limit' in cfg:
		newconf['CELERYD_TASK_SOFT_TIME_LIMIT'] = cfg['task_soft_time_limit']
	if 'state_db' in cfg:
		newconf['CELERYD_STATE_DB'] = cfg['state_db']
	if 'timer_precision' in cfg:
		newconf['CELERYD_TIMER_PRECISION'] = cfg['timer_precision']
	if 'hijack_root_logger' in cfg:
		newconf['CELERYD_HIJACK_ROOT_LOGGER'] = cfg['hijack_root_logger']
	if 'log_color' in cfg:
		newconf['CELERYD_LOG_COLOR'] = cfg['log_color']
	if 'log_format' in cfg:
		newconf['CELERYD_LOG_FORMAT'] = cfg['log_format']
	if 'task_log_format' in cfg:
		newconf['CELERYD_TASK_LOG_FORMAT'] = cfg['task_log_format']
	if 'pool' in cfg:
		newconf['CELERYD_POOL'] = cfg['pool']
	if 'pool_restarts' in cfg:
		newconf['CELERYD_POOL_RESTARTS'] = cfg['pool_restarts']
	if 'autoscaler' in cfg:
		newconf['CELERYD_AUTOSCALER'] = cfg['autoscaler']
	if 'autoreloader' in cfg:
		newconf['CELERYD_AUTORELOADER'] = cfg['autoreloader']
	if 'consumer' in cfg:
		newconf['CELERYD_CONSUMER'] = cfg['consumer']
	if 'timer' in cfg:
		newconf['CELERYD_TIMER'] = cfg['timer']

	if 'celerymon_log_format' in cfg:
		newconf['CELERYMON_LOG_FORMAT'] = cfg['celerymon_log_format']

	if 'broadcast_queue' in cfg:
		newconf['CELERY_BROADCAST_QUEUE'] = cfg['broadcast_queue']
	if 'broadcast_exchange' in cfg:
		newconf['CELERY_BROADCAST_EXCHANGE'] = cfg['broadcast_exchange']
	if 'broadcast_exchange_type' in cfg:
		newconf['CELERY_BROADCAST_EXCHANGE_TYPE'] = cfg['broadcast_exchange_type']

	if 'scheduler' in cfg:
		newconf['CELERYBEAT_SCHEDULER'] = cfg['scheduler']
	if 'schedule_filename' in cfg:
		newconf['CELERYBEAT_SCHEDULE_FILENAME'] = cfg['schedule_filename']
	if 'sync_every' in cfg:
		newconf['CELERYBEAT_SYNC_EVERY'] = cfg['sync_every']
	if 'max_loop_interval' in cfg:
		newconf['CELERYBEAT_MAX_LOOP_INTERVAL'] = cfg['max_loop_interval']

	# FIXME: complex python values!
	opts = make_config_dict(cfg, 'schedule.')
	if len(opts) > 0:
		newconf['CELERYBEAT_SCHEDULE'] = as_dict(opts)

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
	else:
		newconf['CELERY_QUEUES'] = _default_queues

	mm = reg.getUtility(IModuleManager)

	opts = []
	if 'imports' in cfg:
		opts = aslist(cfg['imports'])
	for imp in mm.get_task_imports():
		opts.append(imp)
	if len(opts) > 0:
		newconf['CELERY_IMPORTS'] = opts

	opts = []
	if 'include' in cfg:
		opts = aslist(cfg['include'])
	# FIXME: hook module include here (?)
	if len(opts) > 0:
		newconf['CELERY_INCLUDE'] = opts

	if len(newconf) > 0:
		if isinstance(celery, Celery):
			celery.config_from_object(newconf)
		else:
			celery.update(newconf)

app = Celery('netprofile')

def task_cap(cap):
	def _app_cap_wrapper(wrapped):
		wrapped.__cap__ = cap
		return wrapped

	return _app_cap_wrapper

@celeryd_init.connect
def _setup(conf=None, **kwargs):
	global app

	ini_file='production.ini'
	if 'NP_INI_FILE' in os.environ:
		ini_file = os.environ['NP_INI_FILE']

	ini_name='netprofile'
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

	_parse_ini_settings(cfg.registry, conf)
	app.settings = settings
	app.mmgr = mmgr

def setup_celery(reg):
	_parse_ini_settings(reg, app)

if __name__ == '__main__':
	app.start()

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	_parse_ini_settings(config.registry, app)

