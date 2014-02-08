## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>
<div class="panel panel-default">
 	<div class="panel-heading">${_('Make a future payment')}</div>
    <div class="panel-body" style="line-height: 50%;">
	<div class="alert alert-warning alert-dismissable">
	<button class="close" aria-hidden="true" data-dismiss="alert" type="button">×</button>
	Warning! Makeing this paymend you are promise to pay us in 5 days.
	</div>
		<div class="list-group-item clearfix" style="line-height: 50%;">
			<form class="" role="form" method="post" action="${req.route_url('access.cl.dofuture')}">
					<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
					<input type="text" placeholder="${_('Amount')}" class="form-control" required="required" name="user" title="${_('Fill payment amount here.')}" value="" maxlength="254" tabindex="1" autocomplete="off" />
					<br>
					<button type="submit" class="btn btn-default pull-right" name="submit" title="${_('Make a future payment')}" tabindex="3">${_('Pay')}</button>
			</form>
		</div>
</div>

