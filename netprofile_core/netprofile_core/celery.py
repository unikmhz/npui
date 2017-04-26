#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Core module - Celery scheduler
# © Copyright 2016 Alex 'Unik' Unigovsky
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

	def is_due(self):
		sess = DBSession()
		if self.model not in sess:
			self.model = sess.merge(self.model, load=True)
		if not self.model.enabled:
			return False, 15.0
		return self.schedule.is_due(self.last_run_at)

	def __next__(self):
		sess = DBSession()
		model = self.model

		if model not in sess:
			model = sess.merge(model, load=False)

		model.last_run_time = self._default_now()
		model.run_count += 1
		new = self.__class__(model)
		transaction.commit()
		return new

	next = __next__

class Scheduler(beat.Scheduler):
	"""
	Custom scheduler that uses ORM objects for persistence.
	"""
	Entry = ScheduleEntry

	def __init__(self, *args, **kwargs):
		self._schedule = None
		beat.Scheduler.__init__(self, *args, **kwargs)
		self.max_interval = (kwargs.get('max_interval') or
				self.app.conf.CELERYBEAT_MAX_LOOP_INTERVAL or 15)

	def setup_schedule(self):
		pass

	def get_from_db(self):
		ret = {}
		sess = DBSession()
		for task in sess.query(Task).filter(Task.enabled == True):
			ret[task.name] = self.Entry(task)
		transaction.commit()
		return ret

	def sync(self):
		transaction.commit()
		self._schedule = self.get_from_db()

	@property
	def schedule(self):
		if self._schedule is None:
			self.sync()
		return self._schedule

