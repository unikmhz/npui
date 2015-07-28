#!/usr/bin/env python3.2

from pyramid.paster import get_app
application = get_app(
  '/path/to/production.ini', 'xop')

