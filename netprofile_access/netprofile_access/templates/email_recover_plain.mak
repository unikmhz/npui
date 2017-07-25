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
${_('Hello %s!') % entity.name_given}

${_('You have recently requested a password recovery.')}
% if change_pass:
${_('Your password was automatically changed.')}
${_('Here is your new password:')} ${new_pass}
% elif access.password_plain:
${_('Here is your password:')} ${access.password_plain}
% endif

${_('If you didn\'t request a password recovery please contact support immediately.')}

