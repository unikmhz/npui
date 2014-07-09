import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
	'setuptools',
	'netprofile_core >= 0.3'
]

setup(
	name='netprofile_documents',
	version='0.3',
	description='NetProfile Administrative UI - Documents Module',
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
	test_suite='netprofile_documents',
	install_requires=requires,
	entry_points="""\
		[netprofile.modules]
		documents = netprofile_documents:Module
	""",
	message_extractors={'.' : [
		('**.py', 'python', None),
		('**.pt', 'xml', None),
		('**.mak', 'mako', None)
	]}
)

