## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>

	<div class="jumbotron"><div class="container">
		<h1>${error} <small>${_('Error %d') % req.response.status_code}</small></h1>
% if req.response.status_code == 404:
		<p>
			${_('There is no page with the address you provided.')}
			${_('We\'re really sorry about that.')}
		</p>
% elif req.response.status_code == 403:
		<p>
			${_('You don\'t have the credentials that are required to access this page.')}
% if not req.user:
			${_('Maybe you forgot to log in?')}
% else:
			${_('We\'re really sorry about that.')}
% endif
		</p>
% endif
		<p>${_('You can contact support or try again.')}</p>
		<p class="pull-right">
% if req.referer:
			<a class="btn btn-info btn-lg" role="button" href="${req.referer}" title="${_('Go back from where you came')}">
				<span class="glyphicon glyphicon-backward"></span>
				${_('Go Back')}
			</a>
% endif
% if req.user:
			<a class="btn btn-primary btn-lg" role="button" href="${req.route_url('access.cl.home')}" title="${_('Return to home page')}">
				<span class="glyphicon glyphicon-home"></span>
				${_('Go Home')}
			</a>
% else:
			<a class="btn btn-primary btn-lg" role="button" href="${req.route_url('access.cl.login')}" title="${_('Return to sign in page')}">
				<span class="glyphicon glyphicon-log-in"></span>
				${_('Log In')}
			</a>
% endif
		</p>
	</div></div>

