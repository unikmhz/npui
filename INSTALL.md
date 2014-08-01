NetProfile Installation Instructions
====================================

This document provides general guidelines for setting up NetProfile.

Prerequisites
-------------

Before we begin, let's check if you have all of the following:

1. Linux, BSD, OSX or some other UNIX or UNIX-compatible system.

2. [CPython][python]. Supported versions are 2.7 and 3.2+, but the recommeded
   one is 3.4, as it is the primary development target.

   Note: there is a higher possibility for something to break on non-3.4
   Python, as we haven't implemented proper test suite yet. Send patches!

3. [MySQL][mysql] or [MariaDB][maria] database. Other databases *might* be
   supported in the future, but not currently.

   Minimum required version is 5.1 for MySQL/MariaDB. InnoDB or XtraDB
   must be available.

4. Some way to host WSGI applications. There are multiple options here,
   some of them are:

   * [mod_wsgi](http://code.google.com/p/modwsgi/)
   * [waitress](https://github.com/Pylons/waitress)
   * [Tornado](http://www.tornadoweb.org/en/stable/)
   * [uWSGI](https://github.com/unbit/uwsgi)

5. [Redis server][redis] for session storage, caching and real-time messaging
   support.

Installing OS packages
----------------------

You will need to install some OS packages as dependencies to be able to
compile various needed Python modules later on. Here is the list:

* Generic compilation support packages

  - In Fedora/RHEL/CentOS: package group `@development-tools`
  - In Debian/Ubuntu/Mint: virtual package `build-essential`
  - In Arch: package group `base-devel`
  - In Gentoo: you already have it

* Development package for `libxslt`

  - In Fedora/RHEL/CentOS: package `libxslt-devel`
  - In Debian/Ubuntu/Mint: package `libxslt1-dev`
  - In Arch: package `libxslt`
  - In Gentoo: package `dev-libs/libxslt`

* Development package for `cracklib`

  - In Fedora/RHEL/CentOS: package `cracklib-devel`
  - In Debian/Ubuntu/Mint: package `libcrack2-dev`
  - In Arch: package `cracklib`
  - In Gentoo: package `sys-libs/cracklib`

* Development package for `zlib`

  - In Fedora/RHEL/CentOS: package `zlib-devel`
  - In Debian/Ubuntu/Mint: package `zlib1g-dev`
  - In Arch: package `zlib`
  - In Gentoo: package `sys-libs/zlib`

* Package for `libmagic`

  - In Fedora/RHEL/CentOS: package `file-libs`
  - In Debian/Ubuntu/Mint: package `libmagic1`
  - In Arch: package `file`
  - In Gentoo: package `sys-apps/file`

* Python `virtualenv` package

  - In Fedora/RHEL/CentOS: package `python-virtualenv`
  - In Debian/Ubuntu/Mint: package `python3-virtualenv` or `python-virtualenv`
  - In Arch: package `python-virtualenv` or `python2-virtualenv`
  - In Gentoo: package `dev-python/virtualenv`

Note: You may already have some or all of these installed in your system.
That's totally fine.

Database configuration
----------------------

#### MySQL

*FIXME: Write this*

Creating virtual environment
----------------------------

For production environments it is highly recommended to create separate OS
user and group for running NetProfile. Here's how you do it on Linux (run
this as `root` user):

```sh
groupadd netprofile
useradd -m -d /var/lib/netprofile -g netprofile -c 'NetProfile' netprofile
su - netprofile
```

You are now inside your new user's home directory `/var/lib/netprofile`. Now
create and activate your Python virtual environment:

```sh
virtualenv --python=python3.4 --prompt='[np] ' np
cd np
source ./bin/activate
```

Note: replace python executable in the command above with your version.

You now have a shell inside your newly created virtual environment. Note
the prefix **[np]** before your prompt — it tells you that any Python-related
commands you issue will be executed inside this environment and will not
affect your OS outside. Also note that this is **not** a chroot.

Installing NetProfile Python packages
-------------------------------------

*FIXME: Write this*

```sh
pip install netprofile_core
pip install <add any other needed modules here>
```

NetProfile configuration
------------------------

*FIXME: Write this*

1. Copy .ini
2. Edit .ini
3. `export NP_INI_FILE=/path/to/file.ini`

Installing and enabling NetProfile modules
------------------------------------------

*FIXME: Write this*

```sh
npctl module install all
npctl module enable all
npctl module ls
```

Now what?
---------

*FIXME: TO BE FINISHED*

  [python]: https://www.python.org/
  [mysql]: https://www.mysql.com/
  [maria]: https://mariadb.com/
  [redis]: http://redis.io/

