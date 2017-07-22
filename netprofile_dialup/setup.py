#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Setup script for netprofile_dialup package
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

    'netprofile_core >= 0'
]

setup(
    name='netprofile_dialup',
    version=versioneer.get_version(),
    cmdclass=commands,
    description='NetProfile Administrative UI - Dialup Module',
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
    author='Andriyanov Nikita',
    author_email='nikitos@itws.ru',
    url='https://github.com/unikmhz/npui',
    keywords='web wsgi pyramid np netprofile'
             ' crm billing accounting network isp',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='netprofile_dialup',
    install_requires=requires,
    entry_points={
        'netprofile.modules': [
            'dialup = netprofile_dialup:Module'
        ]
    },
    message_extractors={'.': [
        ('**.py', 'python', None),
        ('**.pt', 'xml', None),
        ('**.mak', 'mako', None)
    ]}
)
