## -*- coding: utf-8 -*-
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${cur_loc}">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge;chrome=1" />
	<meta name="keywords" content="netprofile" />
	<meta name="description" content="NetProfile client UI" />
	<title>NetProfile :: ${_('Password Recovery')}</title>
</head>
<body>
	<div class="block">
		<h1>${_('Hello %s!') % entity.name_given}</h1>

		<p>${_('You have recently requested a password recovery.')}</p>
% if change_pass:
		<p>${_('Your password was automatically changed.')}</p>
		<p>${_('Here is your new password:')} <strong>${access.password}</strong></p>
% else:
		<p>${_('Here is your password:')} <strong>${access.password}</strong></p>
% endif

		<p>${_('If you didn\'t request a password recovery please contact support immediately.')}</p>
	</div>
</body>

