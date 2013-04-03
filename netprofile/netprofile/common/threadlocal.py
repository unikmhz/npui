#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

from netprofile.common import magic as _magic

class TLSMagic(threading.local):
	def __init__(self):
		self.magic = None

	def get(self):
		if self.magic is None:
			m = _magic.open(_magic.MIME | _magic.ERROR)
			if m.load() < 0:
				raise RuntimeError('libMagic load failed')
			self.magic = m
		return self.magic

magic = TLSMagic()

