## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>
% for stash in req.user.parent.stashes:
<div class="panel panel-default">
 	<div class="panel-heading">${stash.name}<a href="${req.route_url('access.cl.stats', stash_id=req.user.stash.id)}" class="btn btn-default pull-right btn-xs">${_('Statistics')}</a></div>
    <div class="panel-body" style="line-height: 50%;">
		<div class="input-group">
			% if stash.amount > 0:
				<span class="label-success input-group-addon" style="color: #FFFFFF; border-color: #3E8F3E; min-width: 80px; max-width: 30%">
		 	% else:
				<span class="label-danger input-group-addon" style="color: #FFFFFF; border-color: #B92C28; min-width: 80px; max-width: 30%">
		 	% endif
			${_('Amount')}</span>
		    <span class="form-control">
				${round(stash.amount,2)}
			</span>
		</div>
		<br>
		<div class="input-group">
			% if stash.credit >= 0:
				<span class="label-success input-group-addon" style="color: #FFFFFF; border-color: #3E8F3E; min-width: 80px; max-width: 30%">
		 	% else:
				<span class="label-danger input-group-addon" style="color: #FFFFFF; border-color: #B92C28; min-width: 80px; max-width: 30%">
		 	% endif
			${_('Credit')}</span>
		    <span class="form-control">
				${round(stash.credit,2)}
			</span>
		</div>
	</div>
	<ul class="nav nav-tabs noscript">
		<li class="active"><a href="#accounts" data-toggle="tab">${_('Accounts')}</a></li>
  	    <li><a href="#payments" data-toggle="tab">${_('Refill')}</a></li>
		<li><a href="#future" data-toggle="tab">${_('Pay later')}</a></li>
	</ul>
	<div class="tab-content no-js">
		<div class="list-group-item">
			<h4 class="list-group-item-heading">${_('Accounts')}</h4>
		</div>
		<div class="tab-pane active" id="accounts">
		% for a in stash.access_entities:
			<div class="list-group-item">
				<h4 class="list-group-item-heading">${a.nick}</h4>
				% if a.next_rate:
					<p class="list-group-item-text">${_('Next Rate')} ${a.next_rate}</p>
				% endif
				<form class="navbar-form list-group-item-text" role="form" method="post" action="${req.route_url('access.cl.chrate')}">
				<div class="form-group">
					<label for="rate" class="sr-only">${_('Rate')}</label>
					<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
					<select class="form-control chosen-select" id="rate" name="rate" title="${_('Rate')}">
% for rate in rates:
						<option label="${rate}" value="${rate.id}"\
% if rate.id == a.rate_id:
 selected="selected"\
% endif
>${rate}</option>
% endfor
					</select>
				<button type="submit" class="btn btn-default" name="submit" title="${_('Change Rate')}" tabindex="3">${_('Change')}</button>
				</div>
				</form>
			</div>
		% endfor
		</div>
		<div class="list-group-item">
			<h4 class="list-group-item-heading">${_('Refill')}</h4>
		</div>
		<div class="tab-pane" id="payments">
			<div class="list-group-item clearfix" style="line-height: 50%;">
				<form class="" role="form" method="post" action="${req.route_url('access.cl.login')}">
						<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
						<input type="text" placeholder="${_('Amount')}" class="form-control" required="required" name="user" title="${_('Fill payment amount here.')}" value="" maxlength="254" tabindex="1" autocomplete="off" />
						<br>
						<button type="submit" class="btn btn-default pull-right" name="submit" title="${_('Log in to your account')}" tabindex="3">${_('Pay')}</button>
				</form>
			</div>
		</div>
		<div class="list-group-item">
			<h4 class="list-group-item-heading">${_('Pay later')}</h4>
		</div>
		<div class="tab-pane" id="future">
		% for a in stash.futures:

			<div class="list-group-item">
				<h4 class="list-group-item-heading">${a.creation_time}</h4>
				<p class="list-group-item-text">${a.difference}</p>
			</div>
		% endfor
			<div class="list-group-item clearfix" style="line-height: 50%;">
			<div class="alert alert-danger alert-dismissable">${_('Warning! Makeing this paymend you are promise to pay us in 5 days.')}</div>
				<form class="" role="form" method="post" action="${req.route_url('access.cl.dofuture')}">
						<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
						<input type="hidden" id="stashid" name="stashid" value="${stash.id}" />
						<input type="text" placeholder="${_('Amount')}" class="form-control" required="required" name="diff" title="${_('Fill payment amount here.')}" value="" maxlength="254" tabindex="1" autocomplete="off" />
						<br>
						<button type="submit" class="btn btn-default pull-right" name="submit" title="${_('Make a future payment')}" tabindex="3">${_('Pay')}</button>
				</form>
			</div>
		</div>
	</div>
</div>
% endfor

