#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Core module - Celery scheduler
# © Copyright 2016-2017 Alex 'Unik' Unigovsky
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

import datetime
import transaction
from celery import (
	beat,
	current_app
)
from celery.utils.time import is_naive

from netprofile.db.connection import DBSession
from .models import Task

_DEFAULT_MAX_INTERVAL = 5 # seconds
_DEFAULT_SYNC_EVERY = 15 # seconds

class ScheduleEntry(beat.ScheduleEntry):
	"""
	Custom schedule entry that uses ORM objects for persistence.
	"""
	def __init__(self, task):
		self.model = task
		self.app = current_app._get_current_object()

		self.name = task.name
		self.task = task.procedure
		self.schedule = task.schedule.schedule

		self.args = task.arguments
		if not isinstance(self.args, list):
			self.args = []
		self.kwargs = task.keyword_arguments
		if not isinstance(self.kwargs, dict):
			self.kwargs = {}
		self.options = task.options
		self.total_run_count = task.run_count

		if not task.last_run_time:
			task.last_run_time = self._default_now()
		self.last_run_at = task.last_run_time
		if not is_naive(self.last_run_at):
			self.last_run_at = self.last_run_at.replace(tzinfo=None)
		self.total_run_count = task.run_count

	def _default_now(self):
		return self.app.now()

	def __next__(self):
		model = self.model
		model.last_run_time = self._default_now()
		model.run_count += 1
		new = self.__class__(model)
		return new

	next = __next__

class Scheduler(beat.Scheduler):
	"""
	Custom scheduler that uses ORM objects for persistence.
	"""
	Entry = ScheduleEntry

	def __init__(self, *args, **kwargs):
		self._schedule = None
		self._sync_needed = {}
		beat.Scheduler.__init__(self, *args, **kwargs)
		self.sync_every = (
			kwargs.get('sync_every') or
			_DEFAULT_SYNC_EVERY
		)
		self.max_interval = (
			kwargs.get('max_interval') or
			self.app.conf.beat_max_loop_interval or
			_DEFAULT_MAX_INTERVAL
		)

	def get_from_db(self):
		ret = {}
		sess = DBSession()
		for task in sess.query(Task).filter(Task.enabled == True):
			sess.expunge(task.schedule)
			sess.expunge(task)
			ret[task.name] = self.Entry(task)
		transaction.commit()
		return ret

	def setup_schedule(self):
		self._schedule = self.get_from_db()

	def reserve(self, entry):
		model = entry.model
		new = next(entry)
		self._sync_needed[model.id] = model
		return new

	def sync(self):
		to_update = []
		sess = DBSession()
		if len(self._sync_needed) > 0:
			sn = self._sync_needed
			for task in sess.query(Task).filter(Task.id.in_(sn.keys())):
				task.last_run_time = sn[task.id].last_run_time
				task.run_count = sn[task.id].run_count
				to_update.append(task)
			self._sync_needed = {}

		self._schedule = self.get_from_db()
		self._heap = None

	@property
	def schedule(self):
		if self._schedule is None:
			self.sync()
		return self._schedule

