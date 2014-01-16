## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>

<div id="wrap">
	<nav class="navbar navbar-default navbar-fixed-top" role="navigation">
		<div class="container">
			<div class="navbar-header">
				<button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#main-navbar">
					<span class="sr-only">${_('Toggle navigation', domain='netprofile_access')}</span>
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
% if req.user:
				<ul class="no-js nav navbar-nav navbar-right">
					<li class="dropdown">
						<a href="#" class="dropdown-toggle" data-toggle="dropdown"><span class="glyphicon glyphicon-user"></span> ${req.user.nick} <b class="caret"></b></a>
						<ul class="dropdown-menu">
							<li><a href="${req.route_url('access.cl.chpass')}">${_('Change Password', domain='netprofile_access')}</a></li>
							<li class="divider"></li>
							<li><a href="${req.route_url('access.cl.logout')}"><span class="glyphicon glyphicon-log-out"></span> ${_('Log Out', domain='netprofile_access')}</a></li>
						</ul>
					</li>
				</ul>
% endif
<%block name="menubar">\
				<ul class="nav navbar-nav navbar-right">
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
						<a href="${req.route_url(item['route'], traverse=())}">${loc.translate(item['text'])}</a>
% endif
					</li>
% endfor
				</ul>
</%block>
				<form class="navbar-form navbar-right langform" role="form" method="get" action="">
				<div class="form-group">
					<label for="__locale" class="sr-only">${_('Language', domain='netprofile_access')}</label>
					<select class="form-control chosen-select" id="__locale" name="__locale" title="${_('Language', domain='netprofile_access')}">
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
${next.body()}
	</div>
</div>

<div id="footer">
	<span class="single-line">Copyright © 2013-2014 <a href="http://netprofile.ru">${_('NetProfile.ru Team', domain='netprofile_access')}</a>.</span>
	<span class="single-line">${_('License:', domain='netprofile_access')} <a href="http://www.gnu.org/licenses/agpl-3.0.html">AGPLv3</a>+</span>
</div>

