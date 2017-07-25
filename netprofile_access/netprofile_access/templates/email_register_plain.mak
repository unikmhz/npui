## -*- coding: utf-8 -*-
##
## NetProfile: Mail template for account registration
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

${_('Thank you for registering an account in our system.')}
${_('Here is your activation link:')}

${req.route_url('access.cl.activate', _query={ 'for' : entity.nick, 'code' : link.value }) | n}

${_('Be sure to follow it before trying to log in.')}

