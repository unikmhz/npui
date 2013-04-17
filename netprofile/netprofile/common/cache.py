#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.settings import asbool
from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE

cache = None

def configure_cache(settings, name=None):
	prefix = 'netprofile.cache.'
	if name is not None:
		prefix = ''.join((prefix, name, '.'))
	else:
		name = 'MAIN'
	return make_region(name=name).configure_from_config(settings, prefix)

