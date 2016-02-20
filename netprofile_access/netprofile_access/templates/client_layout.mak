## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>

<div id="wrap">
	<nav class="navbar navbar-default navbar-fixed-top" role="navigation">
		<div class="container" role="presentation">
			<div class="navbar-header">
				<button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#main-navbar">
					<span class="sr-only">${_('Toggle navigation', domain='netprofile_access')}</span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</button>
				<span class="navbar-brand" href="#" role="banner">
					<span class="large" role="heading" aria-level="1">NetProfile</span>
					<span class="small" role="heading" aria-level="2">${self.title()}</span>
				</span>
			</div>
			<div class="collapse navbar-collapse" id="main-navbar" role="menubar">
				<ul class="no-js nav navbar-nav navbar-right" role="presentation">
<%block name="menubar">\
% for item in menu:
% if item.get('route') and req.matched_route and (item.get('route') == req.matched_route.name):
					<li class="active">
						<a href="#" role="menuitem">${loc.translate(item['text'])}</a>
% elif item.get('route'):
					<li\
% if item.get('cls'):
 class="${item['cls']}"\
% endif
% if item.get('title'):
 title="${loc.translate(item['title'])}"\
% endif
>
						<a href="${req.route_url(item['route'], traverse=())}" role="menuitem">${loc.translate(item['text'])}</a>
% endif
					</li>
% endfor
</%block>
					<li class="dropdown">
						<a href="#" class="dropdown-toggle flag-toggle" data-toggle="dropdown" id="flag-toggle" title="${_('Change Language', domain='netprofile_access')}" role="menuitem" aria-haspopup="true">
							<img src="${req.static_url('netprofile_access:static/img/flags/%s.png' % req.locale_name)}" alt="${_('Currently Selected Language', domain='netprofile_access')}" />
							<b class="caret"></b>
						</a>
						<ul class="dropdown-menu" role="menu" aria-labelledby="flag-toggle">
% for lang in req.locales:
							<li role="presentation"\
% if lang == req.locale_name:
 class="disabled"\
% endif
><a class="lang-select" href="${req.current_route_url(_query={'__locale' : lang})}" role="menuitem" tabindex="-1">
								<img src="${req.static_url('netprofile_access:static/img/flags/%s.png' % lang)}" alt="${req.locales[lang].english_name} [${req.locales[lang].display_name}]" />
								${req.locales[lang].english_name} [${req.locales[lang].display_name}]
							</a></li>
% endfor
						</ul>
					</li>
% if req.user:
					<li class="dropdown">
						<a href="#" class="dropdown-toggle" data-toggle="dropdown" id="user-toggle" title="${_('User Menu', domain='netprofile_access')}" role="menuitem" aria-haspopup="true">
							<span class="glyphicon glyphicon-user"></span>
							${req.user.nick}
							<b class="caret"></b>
						</a>
						<ul class="dropdown-menu" role="menu" aria-labelledby="user-toggle">
							<li role="presentation"><a href="${req.route_url('access.cl.chpass')}" role="menuitem" tabindex="-1">${_('Change Password', domain='netprofile_access')}</a></li>
							<li role="presentation" class="divider"></li>
							<li role="presentation"><a href="${req.route_url('access.cl.logout')}" role="menuitem" tabindex="-1"><span class="glyphicon glyphicon-log-out"></span> ${_('Log Out', domain='netprofile_access')}</a></li>
						</ul>
					</li>
% endif
				</ul>
			</div>
		</div>
	</nav>

	<div class="container" role="main">
% if context.get('crumbs'):
	<nav role="navigation" aria-label="${_('You are here:', domain='netprofile_access') | h}"><ol class="breadcrumb" role="presentation">
% for cr in crumbs:
		<li\
% if 'url' not in cr:
 class="active"\
% endif
>
% if 'url' in cr:
			<a href="${cr['url']}" aria-level="${loop.index + 1}">${cr['text']}</a>
% else:
			<span aria-level="${loop.index + 1}">${cr['text']}</span>
% endif
		</li>
% endfor
	</ol></nav>
% endif
% for msg in req.session.pop_flash():

	<div class="alert alert-${msg['class'] if 'class' in msg else 'success'} alert-dismissable" role="alert">
		<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
		${msg['text']}
	</div>

% endfor
${next.body()}
	</div>
</div>

<div id="footer" role="contentinfo">
	<span class="single-line">Copyright © 2010-2016 <a href="http://netprofile.ru">${_('NetProfile.ru Team', domain='netprofile_access')}</a>.</span>
	<span class="single-line">${_('License:', domain='netprofile_access')} <a href="http://www.gnu.org/licenses/agpl-3.0.html">AGPLv3</a>+</span>
</div>

