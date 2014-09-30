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

* Development packages for Python

  - In Fedora/RHEL/CentOS: package ``python-devel``
  - In Debian/Ubuntu/Mint: package ``python3-dev`` or ``python-dev``
  - In Arch: you already have it if you've installed required Python version
  - In Gentoo: you already have it if you've installed required Python version

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
configure default server and client character sets to be ``utf8``, and also
enable ``event_scheduler`` option, as shown here:

.. code:: INI

   [client]

   ...

   default_character_set = utf8

   [mysql]

   ...

   default_character_set = utf8

   [mysqld]

   ...

   event_scheduler = ON
   character_set_server = utf8

.. note::

   Setting character sets in ``my.cnf`` is not strictly necessary, but it
   makes following configuration steps a bit easier.

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

Installing NetProfile
---------------------

.. note::

   All commands in this and following sections **must** be executed as
   ``netprofile`` user from within a virtual environment, if you use one.

You can now proceed to install NetProfile. You can do it in two different ways:
either installing pre-packaged modules from a `Python package index`_ or
manually from a git repository.

Installing NetProfile Python packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   As of this writing there are no NetProfile packages available from PyPI.
   So your only option might be to install from git, as described in following
   subsection.

To install NetProfile modules for production use, execute following commands:

.. code:: sh

   pip install netprofile_core
   pip install <add any other needed modules here>

Installing NetProfile packages from Git
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, if you want to participate in development or fix a bug, you
can use bundled scripts to manually install all prerequisites and register
module source directories as installed packages. To do that, first check out
main (or your own, forked) repository by running this command from the home
directory of your new user (which will be ``/var/lib/netprofile`` if you've
followed instructions in previous chapter):

.. code:: sh

   git clone https://github.com/unikmhz/npui.git

.. note::

   You will need to have ``git`` application installed to be able to work with
   a repository.

You will now have a new directory called ``npui``, that contains checked-out
code of the NetProfile UI standard modules. Go to this directory (which we will
call "repository root") and execute:

.. code:: sh

   ./generate.sh
   ./develop.sh
   ./gen-locale.sh

NetProfile configuration
------------------------

Next you'll need to choose a path for configuration and WSGI files. You can
create and populate it with the following command:

.. code:: sh

   npctl deploy <chosen deployment path>

.. note::

   This command is not strictly necessary, as you can create or copy all
   files by hand. It is simply a time-saver feature.

This will create a directory at your specified path. After that you can use
``activate-*`` files as an alternative to specifying .ini file paths to
every invocation of ``npctl``. You use it like so:

.. code:: sh

   source <chosen deployment path>/activate-development

.. note::

   These files will also activate the virtual environment that was active
   at the time ``npctl deploy`` command was run.

Next you need to edit .ini files inside your deployment directory. Refer
to comments and links in them for further info. ``npctl deploy`` command
has created two .ini files for you -- one is preconfigured for production
deployment, and the other is for development.

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

Write about pserve, .wsgi files, realtime server etc.

.. _CPython: https://www.python.org/
.. _MySQL: https://www.mysql.com/
.. _MariaDB: https://mariadb.com/
.. _Redis server: http://redis.io/
.. _Python package index: https://pypi.python.org/pypi/

