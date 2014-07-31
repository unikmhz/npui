NetProfile
==========

Copyright © 2010-2014 Alex Unigovsky

Copyright © 2010-2014 NetProfile project contributors

What is this?
-------------

NetProfile is web-based customer relationship management, network configuration
and control system. It is geared towards Internet service providers and IT
departments of large enterprises. It includes:

 * Hierarchical customer database
 * Issue tracker
 * Virtual file system (available from UI or via WebDAV)
 * Network objects database
 * Network access control and accounting (with RADIUS support)
 * Customer portal (integrates into issue tracker and billing)

Some useful features include:

 * Modular, extensible architecture
 * Nearly every module is not hardwired, and can be disabled or replaced
 * Configurable access policies for users/groups
 * Flexible access privileges configuration
 * Automatic [XML-RPC] [xmlrpc] and [JSON-RPC] [jsonrpc] API for all managed
   data
 * Multiple languages support (for both main and customer UIs)

Additional features and components will be published here as they are made
usable.

  [xmlrpc]: http://xmlrpc.scripting.com/default.html
  [jsonrpc]: http://www.jsonrpc.org/

Current status
--------------

Current version is 0.3-alpha. The project is in early stages of development,
although some major subsystems are finished and working.

The most lacking area at the moment is documentation. So please, don't be
shy, ask questions!

Project links
-------------

#### Source repositories

* NetProfile UI: [on GitHub] [npui]

  Contains all the standard modules as well as basic framework for running
  NetProfile WSGI app.

* rlm_np FreeRADIUS module: To be published

  Contains rlm_np module for FreeRADIUS. Used for network access control and
  accounting.

#### Bug tracker

* NetProfile UI: [on GitHub] [npui-it]

  Add bug reports, patches, translations and feature requests here.

#### Mailing lists

* User discussions: [Google Group] [ml-users]

  Everything not appropriate for a bug tracker (i.e. questions, how-tos etc.)
  should be posted here.

  [npui]: https://github.com/unikmhz/npui "NetProfile UI"
  [npui-it]: https://github.com/unikmhz/npui/issues "Issues for NetProfile UI"
  [ml-users]: https://groups.google.com/d/forum/netprofile-users

License
-------

NetProfile is free software: you can redistribute it and/or
modify it under the terms of the [GNU Affero General Public
License] [agpl3] as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later
version.

NetProfile is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General
Public License along with NetProfile. If not, see
[GNU Licenses] [gnulic].

  [agpl3]: http://www.gnu.org/licenses/agpl.html
  [gnulic]: http://www.gnu.org/licenses/

External libraries
------------------

