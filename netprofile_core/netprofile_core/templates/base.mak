## -*- coding: utf-8 -*-
##
## NetProfile: Base HTML template
## Copyright © 2012-2017 Alex Unigovsky
##
## This file is part of NetProfile.
## NetProfile is free software: you can redistribute it and/or
## modify it under the terms of the GNU Affero General Public
## License as published by the Free Software Foundation, either
## version 3 of the License, or (at your option) any later
## version.
##
## NetProfile is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General
## Public License along with NetProfile. If not, see
## <http://www.gnu.org/licenses/>.
##
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${cur_loc | h}">
<head>
	<meta charset="UTF-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=edge;chrome=1" />
	<meta name="keywords" content="netprofile" />
	<meta name="description" content="${_('NetProfile administrative UI') | h}" />
	<title>NetProfile :: <%block name="title">${_('Home') | h}</%block></title>
	<link rel="shortcut icon" href="${req.static_url('netprofile_core:static/favicon.ico')}" />

% for i_css in res_css:
	<link rel="stylesheet" href="${req.static_url(i_css)}" type="text/css" media="screen, projection" />
% endfor
<%block name="head_css"/>

% for i_js in res_js:
	<script type="text/javascript" src="${req.static_url(i_js)}" charset="UTF-8"></script>
% endfor
% if (cur_loc is not None) and (cur_loc != 'en'):
% for i_js in res_ljs:
	<script type="text/javascript" src="${req.static_url(i_js)}" charset="UTF-8"></script>
% endfor
% endif
<%block name="head"/>
</head>
<body>${self.body()}</body>
</html>

