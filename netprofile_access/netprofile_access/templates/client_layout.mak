## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>

<div id="wrap">
	<nav class="navbar navbar-default navbar-fixed-top" role="navigation">
		<div class="container">
			<div class="navbar-header">
				<button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#main-navbar">
					<span class="sr-only">${_('Toggle navigation')}</span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</button>
				<span class="navbar-brand" href="#">
					<span class="large">NetProfile</span>
					<span class="small">${self.title()}</span>
				</span>
			</div>
			<div class="collapse navbar-collapse" id="main-navbar">
<%block name="menubar">\
				<ul class="nav navbar-nav">
% for item in menu:
% if item.get('route') and req.matched_route and (item.get('route') == req.matched_route.name):
					<li class="active">
						<a href="#">${loc.translate(item['text'])}</a>
% elif item.get('route'):
					<li\
% if item.get('cls'):
 class="${item['cls']}"\
% endif
% if item.get('title'):
 title="${loc.translate(item['title'])}"\
% endif
>
						<a href="${req.route_url(item['route'])}">${loc.translate(item['text'])}</a>
% endif
					</li>
% endfor
				</ul>
</%block>
				<form class="navbar-form navbar-right" role="form" method="get" action="">
				<div class="form-group">
					<label for="__locale" class="sr-only">${_('Language')}</label>
					<select class="form-control chosen-select" id="__locale" name="__locale" title="${_('Language')}">
% for lang in langs:
						<option label="${lang[1]}" value="${lang[0]}"\
% if lang[0] == cur_loc:
 selected="selected"\
% endif
>${lang[1]}</option>
% endfor
					</select>
				</div>
				</form>
			</div>
		</div>
	</nav>

	<div class="container">
% for msg in req.session.pop_flash():
	<div class="alert alert-${msg['class'] if 'class' in msg else 'success'} alert-dismissable">
		<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
		${msg['text']}
	</div>
% endfor
% if req.user:
	<div class="btn-toolbar userbar" role="toolbar" style="float: right;">
		<div class="btn-group">
			<span class="form-control">${_('Logged in as')} <strong>${req.user.nick}</strong></span>
		</div>
		<div class="btn-group">
			<a href="${req.route_url('access.cl.chpass')}" class="btn btn-default">${_('Change Password')}</a>
			<a href="${req.route_url('access.cl.logout')}" class="btn btn-danger"><span class="glyphicon glyphicon-log-out"></span> ${_('Log Out')}</a>
		</div>
	</div>
% endif
${next.body()}
	</div>
</div>

<div id="footer">
	<span class="single-line">Copyright © 2013-2014 <a href="http://netprofile.ru">${_('NetProfile.ru Team')}</a>.</span>
	<span class="single-line">${_('License:')} <a href="http://www.gnu.org/licenses/agpl-3.0.html">AGPLv3</a>+</span>
</div>

