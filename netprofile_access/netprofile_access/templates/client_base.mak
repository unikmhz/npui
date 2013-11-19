## -*- coding: utf-8 -*-
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${cur_loc}">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge;chrome=1" />
	<meta name="keywords" content="netprofile" />
	<meta name="description" content="NetProfile client UI" />
	<title>NetProfile :: <%block name="title">${_('User Portal')}</%block></title>
	<link rel="shortcut icon" href="${req.static_url('netprofile_access:static/favicon.ico')}" />
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/client.css')}" type="text/css" media="screen, projection" />
<%block name="head"/>
</head>
<body>${next.body()}</body>
</html>
