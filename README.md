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

First steps
-----------

See `INSTALL.md` for general installation guidelines. `DEVELOP.md` file might
be useful if you want to set up your own development environment.

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

Bundled libraries
-----------------

* [Sencha ExtJS][extjs], licensed under [GPLv3][gpl3]
* [Extensible Calendar Pro][extcal], licensed under [GPLv3][gpl3]
* [Google ipaddr-py][ipaddr], licensed under [Apache 2.0 license][apl20]
* Modified [pyramid_extdirect][pextdir], licensed under following license:

  > Copyright (c) 2010-2011 Igor Stroh, All Rights Reserved
  >
  > Redistribution and use in source and binary forms, with or without
  > modification, are permitted provided that the following conditions are
  > met:
  >
  > 1. Redistributions in source code must retain the accompanying
  >    copyright notice, this list of conditions, and the following
  >    disclaimer.
  >
  > 2. Redistributions in binary form must reproduce the accompanying
  >    copyright notice, this list of conditions, and the following
  >    disclaimer in the documentation and/or other materials provided
  >    with the distribution.
  >
  > 3. Names of the copyright holders must not be used to endorse or
  >    promote products derived from this software without prior
  >    written permission from the copyright holders.
  >
  > 4. If any files are modified, you must cause the modified files to
  >    carry prominent notices stating that you changed the files and
  >    the date of any change.
  >
  > #### Disclaimer
  >
  > THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND
  > ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
  > TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
  > PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
  > HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
  > EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
  > TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
  > DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
  > ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
  > TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
  > THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
  > SUCH DAMAGE.

* [SockJS JavaScript client][sockjs], licensed under [MIT license][sockjs-mit]
* [TinyMCE][mce], licensed under [LGPL 2.1][lgpl21]

  [gpl3]: http://www.gnu.org/licenses/gpl.html
  [lgpl21]: https://www.gnu.org/licenses/lgpl-2.1.html
  [apl20]: http://www.apache.org/licenses/LICENSE-2.0
  [extjs]: http://www.sencha.com/products/extjs/
  [extcal]: http://ext.ensible.com/
  [sockjs]: https://github.com/sockjs/sockjs-client
  [sockjs-mit]: https://github.com/sockjs/sockjs-client/blob/master/LICENSE
  [ipaddr]: http://code.google.com/p/ipaddr-py/
  [pextdir]: https://github.com/jenner/pyramid_extdirect
  [mce]: http://www.tinymce.com/

