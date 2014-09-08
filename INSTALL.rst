NetProfile Installation Instructions
====================================

This document provides general guidelines for setting up NetProfile.

Prerequisites
-------------

Before we begin, let's check if you have all of the following:

1. Linux, BSD, OSX or some other UNIX or UNIX-compatible system.

2. CPython_. Supported versions are 2.7 and 3.2+, but the recommeded one is
   3.4, as it is the primary development target.

   .. note::

      There is a higher possibility for something to break on non-3.4
      Python, as we haven't implemented proper test suite yet. Send patches!

3. MySQL_ or MariaDB_ database. Other databases *might* be supported in
   the future, but not currently.

   Minimum required version is 5.1 for MySQL/MariaDB. InnoDB or XtraDB
   must be available.

4. Some way to host WSGI applications. There are multiple options here,
   some of them are:

   - `mod_wsgi <http://code.google.com/p/modwsgi/>`__
   - `waitress <https://github.com/Pylons/waitress>`__
   - `Tornado <http://www.tornadoweb.org/en/stable/>`__
   - `uWSGI <https://github.com/unbit/uwsgi>`__

5. `Redis server`_ for session storage, caching and real-time messaging
   support.

Installing OS packages
----------------------

You will need to install some OS packages as dependencies to be able to
compile various needed Python modules later on. Here is the list:

* Generic compilation support packages

  - In Fedora/RHEL/CentOS: package group ``@development-tools``
  - In Debian/Ubuntu/Mint: virtual package ``build-essential``
  - In Arch: package group ``base-devel``
  - In Gentoo: you already have it

* Development package for ``libxslt``

  - In Fedora/RHEL/CentOS: package ``libxslt-devel``
  - In Debian/Ubuntu/Mint: package ``libxslt1-dev``
  - In Arch: package ``libxslt``
  - In Gentoo: package ``dev-libs/libxslt``

* Development package for ``cracklib``

  - In Fedora/RHEL/CentOS: package ``cracklib-devel``
  - In Debian/Ubuntu/Mint: package ``libcrack2-dev``
  - In Arch: package ``cracklib``
  - In Gentoo: package ``sys-libs/cracklib``

* Development package for ``zlib``

  - In Fedora/RHEL/CentOS: package ``zlib-devel``
  - In Debian/Ubuntu/Mint: package ``zlib1g-dev``
  - In Arch: package ``zlib``
  - In Gentoo: package ``sys-libs/zlib``

* Package for ``libmagic``

  - In Fedora/RHEL/CentOS: package ``file-libs``
  - In Debian/Ubuntu/Mint: package ``libmagic1``
  - In Arch: package ``file``
  - In Gentoo: package ``sys-apps/file``

* Python ``virtualenv`` package

  - In Fedora/RHEL/CentOS: package ``python-virtualenv``
  - In Debian/Ubuntu/Mint: package ``python3-virtualenv`` or ``python-virtualenv``
  - In Arch: package ``python-virtualenv`` or ``python2-virtualenv``
  - In Gentoo: package ``dev-python/virtualenv``

.. note::

   You may already have some or all of these installed in your system. That's
   totally fine.

Database configuration
----------------------

MySQL
~~~~~

Your MySQL configuration (usually stored in ``/etc/mysql/my.cnf`` file) must
enable ``event_scheduler`` option, as shown here:

.. code:: INI

   [mysqld]

   ...

   event_scheduler = ON

Next, you need to create NetProfile database and user. To do so, log in to
MySQL CLI as ``root`` user (usually done with ``mysql -u root -p``, but whether
the ``-p`` flag is needed depends on your configuration) and execute
the following 4 SQL commands, substituting the password string in the first
one.

.. code:: SQL

   CREATE USER 'np'@'localhost' IDENTIFIED BY 'make-your-own-password-here';
   CREATE DATABASE `np` DEFAULT CHARACTER SET utf8;
   GRANT ALL PRIVILEGES ON np.* TO 'np'@'localhost';
   FLUSH PRIVILEGES;

This will create a user ``np@localhost``, create a database named ``np``,
grant required privileges for the users, and reread them.

Creating virtual environment
----------------------------

For production environments it is highly recommended to create separate OS
user and group for running NetProfile. Here's how you do it on Linux (run
this as ``root`` user):

.. code:: sh

   groupadd netprofile
   useradd -m -d /var/lib/netprofile -g netprofile -c 'NetProfile' netprofile
   su - netprofile

You are now inside your new user's home directory ``/var/lib/netprofile``. Now
create and activate your Python virtual environment:

.. code:: sh

   virtualenv --python=python3.4 --prompt='[np] ' np
   cd np
   source ./bin/activate

.. note::

   Replace python executable in the command above with your version.

You now have a shell inside your newly created virtual environment. Note
the prefix **[np]** before your prompt — it tells you that any Python-related
commands you issue will be executed inside this environment and will not
affect your OS outside. Also note that this is **not** a chroot.

Installing NetProfile Python packages
-------------------------------------

.. note::

   All commands in this section **must** be executed as ``netprofile`` user
   from within a virtual environment, if you use one.

To install NetProfile modules for production use, execute following commands:

.. code:: sh

   pip install netprofile_core
   pip install <add any other needed modules here>

Alternatively, if you want to participate in development or fix a bug, you
can use bundled ``develop.sh`` script to manually install all prerequisites
and register module source directories as installed packages. To do that,
go to the root of a checked out repository and execute:

.. code:: sh

   ./develop.sh

NetProfile configuration
------------------------

*FIXME: Write this. Also, add proper comments to INI files*

1.	Copy .ini
2.	Edit .ini
3.	Use ``export NP_INI_FILE=/path/to/file.ini``

Installing and enabling NetProfile modules
------------------------------------------

*FIXME: Write this*

.. code:: sh

   npctl module install all
   npctl module enable all
   npctl module ls

Now what?
---------

*FIXME: Write this*

Write about pserve, .wsgi files etc.

.. _CPython: https://www.python.org/
.. _MySQL: https://www.mysql.com/
.. _MariaDB: https://mariadb.com/
.. _Redis server: http://redis.io/

