## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>
<%block name="head">\
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/client.js')}"></script>\
</%block>

<div id="wrapper">
	<div id="header">
	${self.title()}
	</div>
	<div id="body">
<%block name="sidebar">\
	<ul id="menu">
% for item in menu:
% if item.get('route') and req.matched_route and (item.get('route') == req.matched_route.name):
		<li class="active">
			${loc.translate(item['text'])}
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
		<li class="flexblock">
		<form method="get" action="${req.route_url('access.cl.register')}">
		<div class="elem">
			<label for="__locale">${_('Language')}</label>
			<div class="wrap">
			<select class="text" id="__locale" name="__locale">
% for lang in langs:
				<option label="${lang[1]}" value="${lang[0]}"\
% if lang[0] == cur_loc:
 selected="selected"\
% endif
>${lang[1]}</option>
% endfor
			</select>
			<button type="submit" id="lang_submit" name="submit" title="${_('Change your current language')}">${_('Change')}</button>
			</div>
		</div>
		</form>
		</li>
	</ul>\
</%block>
	<div id="contents">
${next.body()}
	</div>
	</div>
</div>
<div id="footer">
	Copyright © 2013 <a href="http://netprofile.ru">${_('NetProfile.ru Team')}</a>.
	${_('License:')} <a href="http://www.gnu.org/licenses/agpl-3.0.html">AGPLv3</a>+
</div>

