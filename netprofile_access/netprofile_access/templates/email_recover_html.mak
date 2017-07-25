## -*- coding: utf-8 -*-
##
## NetProfile: Mail template for account password recovery
## Copyright © 2013-2017 Alex Unigovsky
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
		<p>${_('Here is your new password:')} <strong>${new_pass}</strong></p>
% elif access.password_plain:
		<p>${_('Here is your password:')} <strong>${access.password_plain}</strong></p>
% endif

		<p>${_('If you didn\'t request a password recovery please contact support immediately.')}</p>
	</div>
</body>

