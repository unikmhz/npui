## -*- coding: utf-8 -*-
##
## NetProfile: HTML block template for paid services
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
<%!

from netprofile_paidservices.models import PaidServiceQPType

%>\
<%namespace module="netprofile.tpl.filters" import="date_fmt" />\
	<ul class="list-group tab-pane fade" id="tab-paidservices-${stash.id}">
% for ps in stash.paid_services:
% if ps.type.quota_period_type == PaidServiceQPType.independent:
		<li class="list-group-item">
			<div class="pull-right">
% if not ps.active:
				<span class="label label-warning">${_('Inactive')}</span>
% elif not ps.is_paid:
				<span class="label label-danger">${_('Unpaid')}</span>
% endif
			</div>
			<h4 class="list-group-item-heading">${ps.type.name}</h4>
% if ps.type.description:
			<p>${ps.type.description}</p>
% endif
			<div class="row">
				<label for="ps-qpend-${ps.id}" class="col-sm-4">${_('Paid Till', domain='netprofile_paidservices')}</label>
				<div id="ps-qpend-${ps.id}" class="col-sm-8">${ps.quota_period_end | n,date_fmt}</div>
			</div>
		</li>
% endif
% endfor
	</ul>
