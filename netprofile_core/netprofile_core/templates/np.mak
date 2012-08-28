<%!

from pyramid.security import has_permission

%>

<%def name="jscap(code)">\
% if code is None:
true\
% elif has_permission(code, req.context, req):
true\
% else:
false\
% endif
</%def>

