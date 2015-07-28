NetProfile
==========

Copyright © 2010-2015 Alex Unigovsky

Copyright © 2010-2015 NetProfile project contributors

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
* Automatic XML-RPC_ and JSON-RPC_ API for all managed data
* Multiple languages support (for both main and customer UIs)

Additional features and components will be published here as they are made
usable.

.. _XML-RPC: http://xmlrpc.scripting.com/default.html
.. _JSON-RPC: http://www.jsonrpc.org/

Current status
--------------

Current version is 0.3-alpha. The project is in early stages of development,
although some major subsystems are finished and working.

The most lacking area at the moment is documentation. So please, don't be
shy, ask questions!

Project links
-------------

Source repositories
~~~~~~~~~~~~~~~~~~~

* NetProfile UI: `NetProfile UI on GitHub`_

  Contains all the standard modules as well as basic framework for running
  NetProfile WSGI app.

* rlm_np FreeRADIUS module: To be published

  Contains rlm_np module for FreeRADIUS. Used for network access control and
  accounting.

Bug tracker
~~~~~~~~~~~

* NetProfile UI: `NetProfile UI bug tracker`_

  Add bug reports, patches, translations and feature requests here.

Mailing lists
~~~~~~~~~~~~~

* User discussions: `netprofile-users Google Group`_

  Everything not appropriate for a bug tracker (i.e. questions, how-tos etc.)
  should be posted here.

.. _NetProfile UI on GitHub: https://github.com/unikmhz/npui
.. _NetProfile UI bug tracker: https://github.com/unikmhz/npui/issues
.. _netprofile-users Google Group: https://groups.google.com/d/forum/netprofile-users

First steps
-----------

See `INSTALL.rst file <INSTALL.rst>`_ for general installation guidelines.
`DEVELOP.rst file <DEVELOP.rst>`_ might be useful if you want to set up your
own development environment.

License
-------

NetProfile is free software: you can redistribute it and/or
modify it under the terms of the `GNU Affero General Public
License`_ as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later
version.

NetProfile is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General
Public License along with NetProfile. If not, see `GNU Licenses`_.

.. _GNU Affero General Public License: http://www.gnu.org/licenses/agpl.html
.. _GNU Licenses: http://www.gnu.org/licenses/

Bundled third-party libraries
-----------------------------

* `Sencha ExtJS`_ JavaScript framework, licensed under `GPL version 3`_.
* `Extensible Calendar Pro`_ calendar component for ExtJS (ported to
  ExtJS 5), licensed under `GPL version 3`_.
* `Google ipaddr-py`_ module, licensed under `Apache 2.0`_ license.
* Modified pyramid_extdirect_ module, licensed under following license::

   Copyright (c) 2010-2011 Igor Stroh, All Rights Reserved

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are
   met:

   1. Redistributions in source code must retain the accompanying
      copyright notice, this list of conditions, and the following
      disclaimer.

   2. Redistributions in binary form must reproduce the accompanying
      copyright notice, this list of conditions, and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

   3. Names of the copyright holders must not be used to endorse or
      promote products derived from this software without prior
      written permission from the copyright holders.

   4. If any files are modified, you must cause the modified files to
      carry prominent notices stating that you changed the files and
      the date of any change.

   Disclaimer

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND
   ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
   TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
   PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
   HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
   TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
   ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
   TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
   THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
   SUCH DAMAGE.

* `SockJS JavaScript client`_ library, licensed under following license::

   Parts of the code are derived from various open source projects.

   For code derived from Socket.IO by Guillermo Rauch see
   https://github.com/LearnBoost/socket.io/tree/0.6.17#readme.

   Snippets derived from jQuery-JSONP by Julian Aubourg, generic MIT
   license.

   All other code is released on MIT license:

   ====

   The MIT License (MIT)

   Copyright (c) 2011-2012 VMware, Inc.

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.

* TinyMCE_ rich text editor component, licensed under `LGPL version 2.1`_.
* `Ext.ux.form.TinyMCETextArea`_ component, licensed under `LGPL version 3.0`_.
* `ipaddr.js`_ JavaScript library, licensed under following license::

   Copyright (C) 2011 Peter Zotov <whitequark@whitequark.org>

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.

* jQuery_ JavaScript framework, licensed under following license::

   Copyright jQuery Foundation and other contributors, https://jquery.org/

   This software consists of voluntary contributions made by many
   individuals. For exact contribution history, see the revision history
   available at https://github.com/jquery/jquery

   The following license applies to all parts of this software except as
   documented below:

   ====

   Permission is hereby granted, free of charge, to any person obtaining
   a copy of this software and associated documentation files (the
   "Software"), to deal in the Software without restriction, including
   without limitation the rights to use, copy, modify, merge, publish,
   distribute, sublicense, and/or sell copies of the Software, and to
   permit persons to whom the Software is furnished to do so, subject to
   the following conditions:

   The above copyright notice and this permission notice shall be
   included in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
   LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
   OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
   WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

   ====

   All files located in the node_modules and external directories are
   externally maintained libraries used by this software which have their
   own licenses; we recommend you read them, as their terms may differ from
   the terms above.

* `jQuery UI`_ plugin for jQuery_, licensed under following license::

   Copyright jQuery Foundation and other contributors, https://jquery.org/

   This software consists of voluntary contributions made by many
   individuals. For exact contribution history, see the revision history
   available at https://github.com/jquery/jquery-ui

   The following license applies to all parts of this software except as
   documented below:

   ====

   Permission is hereby granted, free of charge, to any person obtaining
   a copy of this software and associated documentation files (the
   "Software"), to deal in the Software without restriction, including
   without limitation the rights to use, copy, modify, merge, publish,
   distribute, sublicense, and/or sell copies of the Software, and to
   permit persons to whom the Software is furnished to do so, subject to
   the following conditions:

   The above copyright notice and this permission notice shall be
   included in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
   LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
   OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
   WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

   ====

   Copyright and related rights for sample code are waived via CC0. Sample
   code is defined as all source code contained within the demos directory.

   CC0: http://creativecommons.org/publicdomain/zero/1.0/

   ====

   All files located in the node_modules and external directories are
   externally maintained libraries used by this software which have their
   own licenses; we recommend you read them, as their terms may differ from
   the terms above.

* `jQuery Actual`_ plugin for jQuery_, licensed under following license::

   Copyright 2011, Ben Lin (http://dreamerslab.com/)

   Permission is hereby granted, free of charge, to any person obtaining
   a copy of this software and associated documentation files (the
   "Software"), to deal in the Software without restriction, including
   without limitation the rights to use, copy, modify, merge, publish,
   distribute, sublicense, and/or sell copies of the Software, and to
   permit persons to whom the Software is furnished to do so, subject to
   the following conditions:

   The above copyright notice and this permission notice shall be
   included in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
   LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
   OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
   WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

* jqBootstrapValidation_ plugin for jQuery_, licensed under following
  license::

   Copyright (c) 2013 David Godfrey

   Permission is hereby granted, free of charge, to any person
   obtaining a copy of this software and associated documentation
   files (the "Software"), to deal in the Software without
   restriction, including without limitation the rights to use,
   copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the
   Software is furnished to do so, subject to the following
   conditions:

   The above copyright notice and this permission notice shall be
   included in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
   OTHER DEALINGS IN THE SOFTWARE.

* `jQuery Iframe Transport`_ plugin for jQuery_, licensed under following
  license::

   The MIT License

   Copyright (c) 2014 Christopher Lenz

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.

* `jQuery File Upload`_ plugin for jQuery_, licensed under MIT_ license.
* Chosen_ plugin for jQuery_, licensed under following license::

   Copyright (c) 2011-2015 by Harvest

   Available for use under the MIT License

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.

* `moment.js`_ JavaScript library, licensed under following license::

   Copyright (c) 2011-2014 Tim Wood, Iskren Chernev, Moment.js contributors

   Permission is hereby granted, free of charge, to any person
   obtaining a copy of this software and associated documentation
   files (the "Software"), to deal in the Software without
   restriction, including without limitation the rights to use,
   copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the
   Software is furnished to do so, subject to the following
   conditions:

   The above copyright notice and this permission notice shall be
   included in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
   OTHER DEALINGS IN THE SOFTWARE.

* `respond.js`_ JavaScript library, licensed under following license::

   Copyright (c) 2012 Scott Jehl

   Permission is hereby granted, free of charge, to any person
   obtaining a copy of this software and associated documentation
   files (the "Software"), to deal in the Software without
   restriction, including without limitation the rights to use,
   copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the
   Software is furnished to do so, subject to the following
   conditions:

   The above copyright notice and this permission notice shall be
   included in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
   OTHER DEALINGS IN THE SOFTWARE.

* `HTML5 Shiv`_ JavaScript library, licensed under MIT_ license.
* Bootstrap_ CSS/JS framework, licensed under following license::

   The MIT License (MIT)

   Copyright (c) 2011-2015 Twitter, Inc

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.

* `Bootstrap DateTimePicker`_ component, licensed under following license::

   The MIT License (MIT)

   Copyright (c) 2015 Jonathan Peterson (@Eonasdan)

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.

Bundled third-party resources
-----------------------------

* Parts of `Fugue icon set`_ by Yusuke Kamiyamane, licensed under
  `Creative Commons Attribution 3.0 Unported`_ license.
* Parts of `Silk icon set`_ by Mark James, licensed under
  `Creative Commons Attribution 2.5 Generic`_ license.
* Parts of `Faenza icon theme`_ by Matthieu James, licensed under
  `GPL version 3`_.

.. _GPL version 3: http://www.gnu.org/licenses/gpl.html
.. _LGPL version 2.1: https://www.gnu.org/licenses/lgpl-2.1.html
.. _LGPL version 3.0: https://www.gnu.org/licenses/lgpl-3.0.html
.. _Apache 2.0: http://www.apache.org/licenses/LICENSE-2.0
.. _MIT: http://opensource.org/licenses/MIT
.. _Creative Commons Attribution 2.5 Generic: http://creativecommons.org/licenses/by/2.5/
.. _Creative Commons Attribution 3.0 Unported: http://creativecommons.org/licenses/by/3.0/
.. _Sencha ExtJS: http://www.sencha.com/products/extjs/
.. _Extensible Calendar Pro: http://ext.ensible.com/
.. _SockJS JavaScript client: https://github.com/sockjs/sockjs-client
.. _Google ipaddr-py: http://code.google.com/p/ipaddr-py/
.. _pyramid_extdirect: https://github.com/jenner/pyramid_extdirect
.. _TinyMCE: http://www.tinymce.com/
.. _Ext.ux.form.TinyMCETextArea: http://www.point-constructor.com/en/tinyta/
.. _ipaddr.js: http://adilapapaya.com/docs/ipaddr.js/
.. _jQuery: https://jquery.com/
.. _jQuery UI: https://jqueryui.com/
.. _jQuery Actual: https://github.com/dreamerslab/jquery.actual
.. _jqBootstrapValidation: http://reactiveraven.github.io/jqBootstrapValidation/
.. _jQuery Iframe Transport: http://cmlenz.github.io/jquery-iframe-transport/
.. _jQuery File Upload: https://blueimp.github.io/jQuery-File-Upload/
.. _Chosen: http://harvesthq.github.io/chosen/
.. _moment.js: http://momentjs.com/
.. _respond.js: https://github.com/scottjehl/Respond
.. _HTML5 Shiv: https://github.com/aFarkas/html5shiv
.. _Bootstrap: http://getbootstrap.com/
.. _Bootstrap DateTimePicker: http://eonasdan.github.io/bootstrap-datetimepicker/
.. _Fugue icon set: http://p.yusukekamiyamane.com/
.. _Silk icon set: http://www.famfamfam.com/lab/icons/silk/
.. _Faenza icon theme: https://code.google.com/p/faenza-icon-theme/

