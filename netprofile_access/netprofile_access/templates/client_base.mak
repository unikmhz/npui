## -*- coding: utf-8 -*-
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${cur_loc}">
<head>
	<meta charset="UTF-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=edge;chrome=1" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0" />
	<meta name="keywords" content="netprofile" />
	<meta name="description" content="NetProfile client UI" />
	<meta name="csrf-token" content="${req.get_csrf()}" />
	<title>NetProfile :: <%block name="title">${_('User Portal')}</%block></title>
	<link rel="shortcut icon" href="${req.static_url('netprofile_access:static/favicon.ico')}" />
% if req.debug_enabled:
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/bootstrap.css')}" type="text/css" />
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/bootstrap-theme.css')}" type="text/css" />
	<!--[if lt IE 9]>
		<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/html5shiv.js')}"></script>
		<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/respond.src.js')}"></script>
	<![endif]-->
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/chosen.jquery.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/bootstrap.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jqBootstrapValidation.js')}"></script>
% else:
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/bootstrap.min.css')}" type="text/css" />
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/bootstrap-theme.min.css')}" type="text/css" />
	<!--[if lt IE 9]>
		<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/html5shiv.min.js')}"></script>
		<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/respond.min.js')}"></script>
	<![endif]-->
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jquery.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/chosen.jquery.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/bootstrap.min.js')}"></script>
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/jqBootstrapValidation.min.js')}"></script>
% endif
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/client.css')}" type="text/css" />
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/client.js')}"></script>
<%block name="head"/>
</head>
<body>${next.body()}</body>
</html>
