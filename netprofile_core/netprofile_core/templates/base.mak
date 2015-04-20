## -*- coding: utf-8 -*-
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${cur_loc | h}">
<head>
	<meta charset="UTF-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=edge;chrome=1" />
	<meta name="referrer" content="none" />
	<meta name="keywords" content="netprofile" />
	<meta name="description" content="NetProfile administrative UI" />
	<title>NetProfile :: <%block name="title">${_('Home') | h}</%block></title>
	<link rel="shortcut icon" href="${req.static_url('netprofile_core:static/favicon.ico')}" />

% for i_css in res_css:
	<link rel="stylesheet" href="${req.static_url(i_css)}" type="text/css" media="screen, projection" />
% endfor

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

