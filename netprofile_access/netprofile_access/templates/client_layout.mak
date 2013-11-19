## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>

<div id="wrapper">
	<div id="header">
	${self.title()}
	</div>
	<div id="body">
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
	</ul>
	<div id="contents">
${next.body()}
	</div>
	</div>
</div>
<div id="footer">
	FOOTER
</div>

