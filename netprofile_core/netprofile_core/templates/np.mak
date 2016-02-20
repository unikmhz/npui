## -*- coding: utf-8 -*-
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

