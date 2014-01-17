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
				<ul class="no-js nav navbar-nav navbar-right">
<%block name="menubar">\
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
</%block>
					<li class="dropdown">
						<a href="#" class="dropdown-toggle flag-toggle" data-toggle="dropdown" id="flag-toggle" title="${_('Change Language')}">
							<img src="${req.static_url('netprofile_access:static/img/flags/%s.png' % req.locale_name)}" alt="${_('Currently Selected Language')}" />
							<b class="caret"></b>
						</a>
						<ul class="dropdown-menu" role="menu" aria-labelledby="flag-toggle">
% for lang in req.locales:
							<li\
% if lang == req.locale_name:
 class="disabled"\
% endif
><a class="lang-select" href="${req.current_route_url(_query={'__locale' : lang})}" role="menuitem" tabindex="-1">
								<img src="${req.static_url('netprofile_access:static/img/flags/%s.png' % lang)}" />
								${req.locales[lang].english_name} [${req.locales[lang].display_name}]
							</a></li>
% endfor
						</ul>
					</li>
% if req.user:
					<li class="dropdown">
						<a href="#" class="dropdown-toggle" data-toggle="dropdown" id="user-toggle" title="${_('User Menu')}">
							<span class="glyphicon glyphicon-user"></span>
							${req.user.nick}
							<b class="caret"></b>
						</a>
						<ul class="dropdown-menu" role="menu" aria-labelledby="user-toggle">
							<li><a href="${req.route_url('access.cl.chpass')}" role="menuitem" tabindex="-1">${_('Change Password', domain='netprofile_access')}</a></li>
							<li class="divider"></li>
							<li><a href="${req.route_url('access.cl.logout')}" role="menuitem" tabindex="-1"><span class="glyphicon glyphicon-log-out"></span> ${_('Log Out', domain='netprofile_access')}</a></li>
						</ul>
					</li>
% endif
				</ul>
			</div>
		</div>
	</nav>

	<div class="container" role="main">
% for msg in req.session.pop_flash():

	<div class="alert alert-${msg['class'] if 'class' in msg else 'success'} alert-dismissable" role="alert">
		<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
		${msg['text']}
	</div>

% endfor
${next.body()}
	</div>
</div>

<div id="footer" role="banner">
	<span class="single-line">Copyright © 2013-2014 <a href="http://netprofile.ru">${_('NetProfile.ru Team', domain='netprofile_access')}</a>.</span>
	<span class="single-line">${_('License:', domain='netprofile_access')} <a href="http://www.gnu.org/licenses/agpl-3.0.html">AGPLv3</a>+</span>
</div>

