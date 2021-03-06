#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Core module - Celery scheduler
# Copyright © 2016-2017 Alex Unigovsky
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

import transaction
from celery import beat
from celery.utils.time import is_naive
from dateutil.tz import (
    tzlocal,
    tzutc
)

from netprofile.db.connection import DBSession
from .models import (
    Task,
    TaskLog
)

_tz_utc = tzutc()
_tz_local = tzlocal()

_DEFAULT_MAX_INTERVAL = 5  # seconds
_DEFAULT_SYNC_EVERY = 15  # seconds


class ScheduleEntry(beat.ScheduleEntry):
    """
    Custom schedule entry that uses ORM objects for persistence.
    """
    def __init__(self, app, task, last_run_at=None):
        self.model = task
        self.app = app

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

        if task.last_run_time:
            stamp = task.last_run_time
            if is_naive(stamp):
                stamp = stamp.replace(tzinfo=_tz_local)
            self.last_run_at = stamp.astimezone(_tz_utc
                                                if self.app.conf.enable_utc
                                                else _tz_local)
        else:
            self.last_run_at = last_run_at or self._default_now()
            task.last_run_time = self.last_run_at.replace(
                    tzinfo=(_tz_utc
                            if self.app.conf.enable_utc
                            else _tz_local)).astimezone(_tz_local)

        if not is_naive(self.last_run_at):
            self.last_run_at = self.last_run_at.replace(tzinfo=None)
        self.total_run_count = task.run_count

    def _default_now(self):
        return self.app.now()

    def __next__(self):
        model = self.model
        model.last_run_time = self._default_now().replace(
            tzinfo=(_tz_utc
                    if self.app.conf.enable_utc
                    else _tz_local)).astimezone(_tz_local)
        model.run_count += 1
        new = self.__class__(self.app, model)
        return new

    next = __next__


class Scheduler(beat.Scheduler):
    """
    Custom scheduler that uses ORM objects for persistence.
    """
    Entry = ScheduleEntry

    def __init__(self, *args, **kwargs):
        self._schedule = None
        self._pending_results = {}
        self._sync_needed = {}
        beat.Scheduler.__init__(self, *args, **kwargs)
        self.sync_every = kwargs.get('sync_every') or _DEFAULT_SYNC_EVERY
        self.max_interval = (kwargs.get('max_interval')
                             or self.app.conf.beat_max_loop_interval
                             or _DEFAULT_MAX_INTERVAL)

    def get_from_db(self):
        ret = {}
        sess = DBSession()
        for task in sess.query(Task).filter(Task.enabled.is_(True)):
            sess.expunge(task.schedule)
            sess.expunge(task)
            lastrun = None
            if self._schedule and task.name in self._schedule:
                lastrun = self._schedule[task.name].last_run_at
            ret[task.name] = self.Entry(self.app, task, last_run_at=lastrun)
        transaction.commit()
        return ret

    def setup_schedule(self):
        self._schedule = self.get_from_db()
        self.install_default_entries(self._schedule)

    def reserve(self, entry):
        model = entry.model
        new = next(entry)
        self._sync_needed[model.id] = model
        return new

    def sync(self):
        to_update = []
        sess = DBSession()
        if len(self._pending_results) > 0:
            task_uuids = [k
                          for k, v
                          in self._pending_results.items()
                          if v.ready()]
            if len(task_uuids) > 0:
                for log in sess.query(TaskLog).filter(
                        TaskLog.celery_id.in_(task_uuids)):
                    log.update(self._pending_results[log.celery_id])
                    to_update.append(log)
                    del self._pending_results[log.celery_id]
        if len(self._sync_needed) > 0:
            sn = self._sync_needed
            for task in sess.query(Task).filter(Task.id.in_(sn.keys())):
                task.last_run_time = sn[task.id].last_run_time
                task.run_count = sn[task.id].run_count
                to_update.append(task)
            self._sync_needed = {}

        self._schedule = self.get_from_db()
        self.install_default_entries(self._schedule)
        self._heap = None

    @property
    def schedule(self):
        if self._schedule is None:
            self.sync()
        return self._schedule

    def apply_async(self, entry, producer=None, advance=True, **kwargs):
        res = super(Scheduler, self).apply_async(entry, producer,
                                                 advance, **kwargs)
        model = entry.model

        if model.log_executions:
            sess = DBSession()
            log = model.new_result(res)
            sess.add(log)
            self._pending_results[log.celery_id] = res
            transaction.commit()

        return res
