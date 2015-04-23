#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README_LOCAL = open(os.path.join(here, 'README.rst')).read()
README_GLOBAL = open(os.path.join(here, 'README-NP.rst')).read()

requires = [
	'setuptools',
	'python-dateutil',
	'icalendar',
	'phpserialize',
	'dogpile.cache >= 0.4.1',
	'repoze.tm2',

	'SQLAlchemy >= 1.0',
	'zope.sqlalchemy',
	'transaction',

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

	'cliff >= 1.7.0',

	'tornado',
	'sockjs-tornado',
	'tornado-redis',
	'tornado-celery',

	'celery >= 3.1',
	'msgpack-python >= 0.4',

	'reportlab >= 3.1'
]

setup(
	name='netprofile',
	version='0.3',
	description='NetProfile Administrative UI',
	license='GNU Affero General Public License v3 or later (AGPLv3+)',
	long_description=README_LOCAL + '\n\n' +  README_GLOBAL,
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
	url='https://github.com/unikmhz/npui',
	keywords='web wsgi pyramid np netprofile crm billing accounting network isp',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	test_suite='netprofile',
	install_requires=requires,
	entry_points={
		'paste.app_factory' : [
			'main = netprofile:main'
		],
		'console_scripts' : [
			'npctl = netprofile.scripts.ctl:main',
			'np_rtd = netprofile.scripts.rtd:main'
		],
		'netprofile.cli.commands' : [
			'module list = netprofile.cli:ListModules',
			'module ls = netprofile.cli:ListModules',

			'module show = netprofile.cli:ShowModule',
			'module info = netprofile.cli:ShowModule',

			'module install = netprofile.cli:InstallModule',
			'module uninstall = netprofile.cli:UninstallModule',
			'module enable = netprofile.cli:EnableModule',
			'module disable = netprofile.cli:DisableModule',

			'deploy = netprofile.cli:Deploy'
		],
		'netprofile.export.formats' : [
			'csv = netprofile.export.csv:CSVExportFormat',
			'pdf = netprofile.export.pdf:PDFExportFormat'
		]
	}
)

