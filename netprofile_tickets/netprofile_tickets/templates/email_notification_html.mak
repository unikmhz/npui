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
<%inherit file="netprofile_core:templates/email_htmlbase.mak"/>\
<%namespace module="netprofile.tpl.filters" import="date_fmt_short" />\
<%block name="title">${event_text}</%block>\
<%block name="footer">${_('Please keep ticket ID in the subject when replying.')}</%block>\
<%self:mail_block>
	<%self:mail_heading>${event_text}</%self:mail_heading>
	<%self:mail_onecol>
		<dl>
			<dt>${_('Name')}</dt>
			<dd>${ticket.name}</dd>
%if change and change.transition:
			<dt>${_('Transition')}</dt>
			<dd>${change.transition}</dd>
			<dt>${_('State')}</dt>
			<dd>${change.transition.to_state}</dd>
%else:
			<dt>${_('State')}</dt>
			<dd>${ticket.state}</dd>
%endif
			<dt>${_('Entity')}</dt>
			<dd>${ticket.entity}</dd>
%if ticket.assigned_time:
			<dt>${_('Due')}</dt>
			<dd>${ticket.assigned_time | n,date_fmt_short}</dd>
%endif
		</dl>
	</%self:mail_onecol>
%if change and change.comments:
	<%self:mail_onecol>
		${change.comments}
	</%self:mail_onecol>
%elif not change and ticket.description:
	<%self:mail_onecol>
		${ticket.description}
	</%self:mail_onecol>
%endif
</%self:mail_block>

