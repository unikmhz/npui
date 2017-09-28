## -*- coding: utf-8 -*-
##
## NetProfile: HTML template for accounts report
## Copyright © 2014-2017 Alex Unigovsky
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
<%inherit file="netprofile_access:templates/client_layout.mak"/>\
<%namespace module="netprofile.common.hooks" import="gen_block" />\
<%namespace module="netprofile.tpl.filters" import="date_fmt" />\
<%block name="title">${_('My Accounts')}</%block>

% if sname:
<h1>${sname}</h1>
% else:
<h1>${_('My Accounts')}</h1>
% endif

% for stash in stashes:
% if not sname:
<h3 title="${_('Account Name')}">${stash.name}</h3>
% endif
<div class="row">
	<div class="col-sm-4">
		<h4 class="money">
			<span class="balance${' negative' if (stash.amount < 0) else ''}" title="${_('Current account balance')}">
				${stash.formatted_amount(req)}
			</span>
% if stash.credit != 0:
			<small class="single-line">
				${_('Credit:')}
				<span class="balance${' negative' if (stash.credit < 0) else ''}" title="${_('Current credit limit for this account')}">
					${stash.formatted_credit(req)}
				</span>
			</small>
% endif
		</h4>
	</div>
	<div class="col-sm-8" style="padding-bottom: 0.6em;">
	<noscript>
		<div class="btn-group pull-right no-js">
			<button type="button" class="btn btn-link dropdown-toggle" data-toggle="dropdown" title="${_('Actions')}" id="menu-reports-nojs-${stash.id}">
				${_('Actions')}
				<span class="caret"></span>
			</button>
			<ul class="dropdown-menu pull-right" role="menu" aria-labelledby="menu-reports-${stash.id}" aria-expanded="false" aria-hidden="true">
				<li role="presentation" class="disabled"><a role="menuitem" tabindex="-1" href="#">${_('Create User')}</a></li>
				<li role="presentation" class="disabled"><a role="menuitem" tabindex="-1" href="#">${_('Transfer Funds')}</a></li>
				<li role="presentation" class="divider"></li>
				<li role="presentation"><a role="menuitem" tabindex="-1" href="${req.route_url('stashes.cl.accounts', traverse=(stash.id, 'ops'))}">${_('Operations Report')}</a></li>
				<li role="presentation" class="disabled"><a role="menuitem" tabindex="-1" href="#">${_('Promised Payments Report')}</a></li>
${gen_block('stashes.cl.block.menu', stash=stash) | n}
			</ul>
		</div>
	</noscript>
	<ul class="nav nav-tabs">
		<li class="active"><a href="#tab-users-${stash.id}" data-toggle="tab">${_('Users')}</a></li>
% for tabname, tabtitle in extra_tabs.items():
		<li><a href="#tab-${tabname}-${stash.id}" data-toggle="tab">${tabtitle}</a></li>
% endfor
		<li><a href="#tab-replenish-${stash.id}" data-toggle="tab">${_('Replenish')}</a></li>
		<li class="dropdown pull-right">
			<a class="dropdown-toggle" data-toggle="dropdown" id="menu-reports-${stash.id}" href="#">
				${_('Actions')}
				<span class="caret"></span>
			</a>
			<ul class="dropdown-menu pull-right" role="menu" aria-labelledby="menu-reports-${stash.id}" aria-expanded="false" aria-hidden="true">
				<li role="presentation" class="disabled"><a role="menuitem" tabindex="-1" href="#">${_('Create User')}</a></li>
				<li role="presentation" class="disabled"><a role="menuitem" tabindex="-1" href="#">${_('Transfer Funds')}</a></li>
				<li role="presentation" class="divider"></li>
				<li role="presentation"><a role="menuitem" tabindex="-1" href="${req.route_url('stashes.cl.accounts', traverse=(stash.id, 'ops'))}">${_('Operations Report')}</a></li>
				<li role="presentation" class="disabled"><a role="menuitem" tabindex="-1" href="#">${_('Promised Payments Report')}</a></li>
${gen_block('stashes.cl.block.menu', stash=stash) | n}
			</ul>
		</li>
	</ul>
	</div>
</div>
<div class="tab-content">
% if len(stash.access_entities):
	<ul class="list-group tab-pane fade in active" id="tab-users-${stash.id}">
% for a in stash.access_entities:
% if a.alias_of_id == None:
		<li class="list-group-item">
			<h4 class="list-group-item-heading">
				${a.nick}
				<div class="btn-group no-js">
					<button type="button" class="btn btn-link dropdown-toggle" data-toggle="dropdown" title="${_('Actions')}" id="menubtn-user-${a.id}">
						<span class="glyphicon glyphicon-cog"></span>
					</button>
					<ul class="dropdown-menu" role="menu" aria-labelledby="menubtn-user-${a.id}">
${gen_block('stashes.cl.block.entity_menu', stash=stash, a=a) | n}
					</ul>
				</div>
% if a.access_state:
				<span class="label label-danger pull-right">${a.access_state_string(req)}</span>
% endif
			</h4>
% if a.quota_period_end:
			<div class="row">
				<label for="fld-qpend-${stash.id}" class="col-sm-4">${_('Paid Till')}</label>
				<div id="fld-qpend-${stash.id}" class="col-sm-8">${a.quota_period_end | n,date_fmt}</div>
			</div>
% endif
${gen_block('stashes.cl.block.info', stash=stash, a=a) | n}
		</li>
% endif
% endfor
${gen_block('stashes.cl.block.users', stash=stash) | n}
	</ul>
% else:
	<div class="well tab-pane fade in active" id="tab-users-${stash.id}">${_('This account has no users.')}</div>
% endif
	<ul class="list-group tab-pane fade" id="tab-replenish-${stash.id}">
${gen_block('stashes.cl.block.payment', stash=stash) | n}
% if stash.credit == 0:
		<li class="list-group-item">
			<form class="row" role="form" method="post" action="${req.route_url('stashes.cl.accounts', traverse=(stash.id, 'promise'))}">
				<label for="" class="col-sm-4">${_('Promise Payment')}</label>
				<div class="col-sm-8 form-inline">
					<input type="hidden" name="csrf" value="${req.get_csrf()}" />
					<input type="hidden" name="stashid" value="${stash.id}" />
					<input type="text" placeholder="${_('Enter sum')}" class="form-control" required="required" name="diff" title="${_('Enter the sum you promise to pay at a later date.')}" value="" tabindex="-1" autocomplete="off" />
					<button class="btn btn-default" type="submit" name="submit" title="${_('Press to promise payment')}">${_('Promise')}</button>
				</div>
			</form>
		</li>
% else:
		<li class="list-group-item">
			<p class="list-group-item-text">${_('This account already has active promised payment')}</p>
		</li>
% endif
	</ul>
${gen_block('stashes.cl.block.tabs', stash=stash) | n}
</div>
% endfor

