#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Core module - Tasks
# Copyright © 2017 Alex Unigovsky
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

from pyramid.i18n import TranslationStringFactory
from pyramid.settings import asbool
from repoze.sendmail.queue import QueueProcessor
from repoze.sendmail.mailer import SMTPMailer

from netprofile.celery import (
    app,
    task_meta
)
from netprofile.common.util import make_config_dict

_ = TranslationStringFactory('netprofile_core')


@task_meta(cap='BASE_ADMIN',
           title=_('Send queued mail'))
@app.task
def task_send_queued_mail():
    cfg = make_config_dict(app.settings, 'mail.')
    tls = cfg.get('tls')
    if tls is not None:
        tls = asbool(tls)
    mailer = SMTPMailer(hostname=cfg.get('host', 'localhost'),
                        port=int(cfg.get('port', 25)),
                        username=cfg.get('username'),
                        password=cfg.get('password'),
                        no_tls=tls is False,
                        force_tls=tls is True,
                        ssl=asbool(cfg.get('ssl', False)),
                        debug_smtp=asbool(cfg.get('debug', False)))
    maildir = cfg['queue_path']

    qp = QueueProcessor(mailer, maildir, ignore_transient=True)
    qp.send_messages()
