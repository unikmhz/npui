#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
	'setuptools',
	'python-dateutil',
	'icalendar',
	'phpserialize',
	'dogpile.cache >= 0.4.1',
	'repoze.tm2',

	'SQLAlchemy >= 0.8',
	'zope.sqlalchemy',
	'transaction',
	'colander >= 0.9.6',

	'waitress >= 0.7',
	'pyramid >= 1.5a1',
	'pyramid_mako >= 0.3',
	'pyramid_rpc >= 0.5.2',
	'pyramid_debugtoolbar >= 1.0',
	'pyramid_redis_sessions >= 0.9b5',
	'pyramid_mailer >= 0.13',
	'Babel',
	'lingua',
	'lxml',

	'tornado',
	'sockjs-tornado',
	'tornado-redis'
]

setup(
	name='netprofile',
	version='0.3',
	description='NetProfile Administrative UI',
	license='GNU Affero General Public License v3 or later (AGPLv3+)',
	long_description=README + '\n\n' +  CHANGES,
	classifiers=[
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: Implementation :: CPython',
		'Framework :: Pyramid',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
		'Topic :: Office/Business :: Groupware',
		'Topic :: Office/Business :: Scheduling',
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Customer Service',
		'Intended Audience :: Information Technology',
		'Intended Audience :: System Administrators',
		'Intended Audience :: Telecommunications Industry',
		'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
		'Operating System :: OS Independent'
	],
	author='Alex Unigovsky',
	author_email='unik@compot.ru',
	url='https://netprofile.ru',
	keywords='web wsgi pyramid np netprofile crm billing accounting network isp',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	test_suite='netprofile',
	install_requires=requires,
	entry_points="""\
		[paste.app_factory]
		main = netprofile:main
		[console_scripts]
		np_createdb = netprofile.scripts.createdb:main
		np_dropdb = netprofile.scripts.dropdb:main
		np_rtd = netprofile.scripts.rtd:main
		[netprofile.modules]
	""",
)

