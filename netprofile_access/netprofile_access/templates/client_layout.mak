## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>

<div id="wrap">
	<div class="navbar navbar-default navbar-fixed-top" role="navigation">
		<div class="container">
			<div class="navbar-header">
				<button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#main-navbar">
					<span class="sr-only">${_('Toggle navigation')}</span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</button>
				<span class="navbar-brand" href="#">${self.title()}</span>
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
				<ul class="nav navbar-nav navbar-right">
					<li><a href="${req.route_url('access.cl.logout')}">${_('Log Out')}</a></li>
				</ul>
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
	</div>

	<div class="container">${next.body()}</div>
</div>

<div id="footer">
	Copyright © 2013 <a href="http://netprofile.ru">${_('NetProfile.ru Team')}</a>.
	${_('License:')} <a href="http://www.gnu.org/licenses/agpl-3.0.html">AGPLv3</a>+
</div>

