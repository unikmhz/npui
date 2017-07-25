## -*- coding: utf-8 -*-
##
## NetProfile: Template macros for Mako
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
<%def name="jscap(code)">\
% if code is None:
true\
% elif req.has_permission(code):
true\
% else:
false\
% endif
</%def>

<%def name="limit(cap=None,xcap=None)">\
% if ((cap is None) or ((cap is not None) and req.has_permission(cap))) and ((xcap is None) or ((xcap is not None) and (not req.has_permission(xcap)))):
${caller.body()}
% endif
</%def>

