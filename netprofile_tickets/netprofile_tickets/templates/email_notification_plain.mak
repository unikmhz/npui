## -*- coding: utf-8 -*-
##
## NetProfile: Mail template for ticket notification
## Copyright © 2017 Alex Unigovsky
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
<%namespace module="netprofile.tpl.filters" import="date_fmt_short" />\
${event_text}
=======================================================================


${_('Name')}: ${ticket.name}
%if change and change.transition:
${_('Transition')}: ${change.transition}
${_('State')}: ${change.transition.to_state}
%else:
${_('State')}: ${ticket.state}
%endif
${_('Entity')}: ${ticket.entity}
%if ticket.assigned_time:
${_('Due')}: ${ticket.assigned_time | n,date_fmt_short}
%endif


%if change and change.comments:
${change.comments}
%elif not change and ticket.description:
${ticket.description}
%endif

=======================================================================
${_('Please keep ticket ID in the subject when replying.')}
