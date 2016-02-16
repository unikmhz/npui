## -*- coding: utf-8 -*-
<%!

from netprofile.tpl.filters import jsone_compact

%>\
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${cur_loc}">
<head>
	<meta charset="UTF-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=edge;chrome=1" />
	<meta name="referrer" content="none" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0" />
	<meta name="keywords" content="netprofile" />
	<meta name="description" content="NetProfile client UI" />
	<meta name="csrf-token" content="${req.get_csrf()}" />
% if context.get('trans'):
	<!-- ${trans} -->
	<meta name="js-translations" content="${trans | n,jsone_compact,h}" />
% endif
	<title>NetProfile :: <%block name="title">${_('User Portal', domain='netprofile_access')}</%block></title>
	<link rel="shortcut icon" href="${req.static_url('netprofile_access:static/favicon.ico')}" />
% if req.debug_enabled:
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/bootstrap.css')}" type="text/css" />
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/bootstrap-theme.css')}" type="text/css" />
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/bootstrap-datetimepicker.css')}" type="text/css" />
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/font-awesome.css')}" type="text/css" />
	<noscript><link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/jquery.fileupload-noscript.css')}" type="text/css" /></noscript>
	<noscript><link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/jquery.fileupload-ui-noscript.css')}" type="text/css" /></noscript>
% else:
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/bootstrap.min.css')}" type="text/css" />
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/bootstrap-theme.min.css')}" type="text/css" />
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/bootstrap-datetimepicker.min.css')}" type="text/css" />
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/font-awesome.min.css')}" type="text/css" />
	<noscript><link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/jquery.fileupload-noscript.css')}" type="text/css" /></noscript>
	<noscript><link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/jquery.fileupload-ui-noscript.css')}" type="text/css" /></noscript>
% endif
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/client.css')}" type="text/css" />
	<noscript><link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/client-noscript.css')}" type="text/css" /></noscript>
<%block name="head_css"/>
% if req.debug_enabled:
	<!--[if lt IE 9]>
		<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/html5shiv.js')}"></script>
		<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/respond.src.js')}"></script>
	<![endif]-->
% if comb_js:
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/all.js')}"></script>
% else:
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.actual.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.ui.widget.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/chosen.jquery.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/moment.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/bootstrap.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/bootstrap-datetimepicker.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jqBootstrapValidation.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.iframe-transport.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.fileupload.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.fileupload-process.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.fileupload-validate.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.fileupload-ui.js')}"></script>
% endif
% else:
	<!--[if lt IE 9]>
		<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/html5shiv.min.js')}"></script>
		<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/respond.min.js')}"></script>
	<![endif]-->
% if comb_js:
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/all.min.js')}"></script>
% else:
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.actual.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.ui.widget.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/chosen.jquery.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/moment.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/bootstrap.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/bootstrap-datetimepicker.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jqBootstrapValidation.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.iframe-transport.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.fileupload.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.fileupload-process.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.fileupload-validate.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.fileupload-ui.min.js')}"></script>
% endif
% endif
% if not comb_js:
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/client.js')}"></script>
% endif
<%block name="head"/>
</head>
<body>${next.body()}</body>
</html>
