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

<%def name="limit(cap=None,xcap=None)">\
% if ((cap is None) or ((cap is not None) and has_permission(cap, req.context, req))) and ((xcap is None) or ((xcap is not None) and (not has_permission(xcap, req.context, req)))):
${caller.body()}
% endif
</%def>

