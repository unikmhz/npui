## -*- coding: utf-8 -*-
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${cur_loc}">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge;chrome=1" />
	<meta name="keywords" content="netprofile" />
	<meta name="description" content="NetProfile client UI" />
	<title>NetProfile :: ${_('User Activation')}</title>
</head>
<body>
	<div class="block">
	<h1>${_('Hello %s!') % entity.name_given}</h1>

	<p>${_('Thank you for registering an account in our system.')}</p>
	<p>${_('Here is your activation link:')}</p>

	<p>
		<a href="${req.route_url('access.cl.activate', _query={ 'for' : entity.nick, 'code' : link.value }) | n}">${req.route_url('access.cl.activate', _query={ 'for' : entity.nick, 'code' : link.value })}</a>
	</p>

	<p>${_('Be sure to follow it before trying to log in.')}</p>
	</div>
</body>

