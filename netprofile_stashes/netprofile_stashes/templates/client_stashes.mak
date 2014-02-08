## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>\
<%namespace module="netprofile.common.hooks" import="gen_block" />\
<%namespace module="netprofile.tpl.filters" import="date_fmt, curr_fmt" />\
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
				<span class="fa fa-rub"></span>
				${stash.amount | n,curr_fmt}
			</span>
% if stash.credit != 0:
			<small class="single-line">
				${'Credit:'}
				<span class="balance${' negative' if (stash.credit < 0) else ''}" title="${_('Current credit limit for this account')}">
					<span class="fa fa-rub"></span>
					${stash.credit | n,curr_fmt}
				</span>
			</small>
% endif
		</h4>
	</div>
	<div class="col-sm-8" style="padding-bottom: 0.6em;"><ul class="nav nav-tabs">
		<li class="active"><a href="#tab-users-${stash.id}" data-toggle="tab">${_('Users')}</a></li>
  	    <li><a href="#tab-replenish-${stash.id}" data-toggle="tab">${_('Replenish')}</a></li>
		<li class="dropdown pull-right">
			<a class="dropdown-toggle" data-toggle="dropdown" id="menu-reports-${stash.id}" href="#">
				${_('Actions')}
				<span class="caret"></span>
			</a>
			<ul class="dropdown-menu pull-right" role="menu" aria-labelledby="menu-reports-${stash.id}" aria-expanded="false" aria-hidden="true">
				<li role="presentation"><a role="menuitem" tabindex="-1" href="#">${_('Create User')}</a></li>
				<li role="presentation"><a role="menuitem" tabindex="-1" href="#">${_('Transfer Funds')}</a></li>
				<li role="presentation" class="divider"></li>
				<li role="presentation"><a role="menuitem" tabindex="-1" href="${req.route_url('stashes.cl.accounts', traverse=(stash.id, 'ops'))}">${_('Operations Report')}</a></li>
				<li role="presentation"><a role="menuitem" tabindex="-1" href="#">${_('Promised Payments Report')}</a></li>
${gen_block('stashes.cl.block.menu', stash=stash) | n}
			</ul>
		</li>
	</ul></div>
</div>
<div class="tab-content">
% if len(stash.access_entities):
	<ul class="list-group tab-pane fade in active" id="tab-users-${stash.id}">
% for a in stash.access_entities:
% if a.alias_of_id == None:
		<li class="list-group-item">
			<h4 class="list-group-item-heading">
				${a.nick}
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
	</ul>
</div>
% endfor

