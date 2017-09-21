#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Setup script for netprofile package
# Copyright © 2013-2017 Alex Unigovsky
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

import os
from setuptools import setup, find_packages
import versioneer

commands = versioneer.get_cmdclass().copy()
here = os.path.abspath(os.path.dirname(__file__))
README_LOCAL = open(os.path.join(here, 'README.rst')).read()
README_GLOBAL = open(os.path.join(here, 'README-NP.rst')).read()

requires = [
    'setuptools >= 36.0',
    'future >= 0.16',
    'six >= 1.10',
    'packaging >= 16.8',
    'python-dateutil >= 2.6',
    'dogpile.cache >= 0.6',
    'repoze.tm2 >= 2.1',
    'pyparsing >= 2.2',

    'SQLAlchemy >= 1.1.11',
    'zope.sqlalchemy >= 0.7.7',
    'transaction >= 2.1',
    'alembic >= 0.9',

    'waitress >= 1.0.2',
    'pyramid >= 1.9',
    'pyramid_mako >= 1.0.2',
    'pyramid_rpc >= 0.8',
    'pyramid_debugtoolbar >= 4.2.1',
    'pyramid_redis_sessions >= 1.0',
    'pyramid_mailer >= 0.15',
    'Babel >= 2.5.1',
    'lingua >= 4.13',
    'lxml >= 3.8',

    'cliff >= 2.8',

    'tornado >= 4.5.1',
    'sockjs-tornado >= 1.0.3',
    'tornado-redis >= 2.4.18',

    'celery >= 4.0',
    'msgpack-python >= 0.4',

    'scrypt >= 0.8',

    'reportlab >= 3.4',
    'svglib >= 0.8.1'
]
extras_require = {
    ':python_version<"3.2"': [
        'backports.ssl_match_hostname',
        'functools32'
    ],
    ':python_version<"3.3"': [
        'ipaddress'
    ]
}

setup_requires = [
    'pytest-runner'
]

tests_require = [
    'pytest',
    'netprofile_core'
]

setup(
    name='netprofile',
    version=versioneer.get_version(),
    cmdclass=commands,
    description='NetProfile Administrative UI',
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    long_description=README_LOCAL + '\n\n' + README_GLOBAL,
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
        'License :: OSI Approved '
        ':: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent'
    ],
    author='Alex Unigovsky',
    author_email='unik@itws.ru',
    url='https://github.com/unikmhz/npui',
    keywords='web wsgi pyramid np netprofile'
             ' crm billing accounting network isp',
    packages=find_packages(exclude=['tests', 'htmlcov']),
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    tests_require=tests_require,
    setup_requires=setup_requires,
    install_requires=requires,
    extras_require=extras_require,
    entry_points={
        'paste.app_factory': [
            'main = netprofile:main'
        ],
        'console_scripts': [
            'npctl = netprofile.scripts.ctl:main'
        ],
        'netprofile.cli.commands': [
            'module list = netprofile.cli:ListModules',
            'module ls = netprofile.cli:ListModules',

            'module show = netprofile.cli:ShowModule',
            'module info = netprofile.cli:ShowModule',

            'module install = netprofile.cli:InstallModule',
            'module upgrade = netprofile.cli:UpgradeModule',
            'module uninstall = netprofile.cli:UninstallModule',
            'module enable = netprofile.cli:EnableModule',
            'module disable = netprofile.cli:DisableModule',

            'alembic = netprofile.cli:Alembic',
            'db revision = netprofile.cli:DBRevision',

            'deploy = netprofile.cli:Deploy',

            'rt = netprofile.cli:RTServer'
        ],
        'netprofile.export.formats': [
            'csv = netprofile.export.csv:CSVExportFormat',
            'pdf = netprofile.export.pdf:PDFExportFormat'
        ]
    }
)
