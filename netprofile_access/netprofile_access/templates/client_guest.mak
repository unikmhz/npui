## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>
<%block name="title">${_('Register')}</%block>
<%block name="sidebar">\
	<ul id="menu">
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
		<li class="bottom"><a href="${req.route_url('access.cl.login')}" title="${_('Go back to login page')}">${_('Already Registered')}</a></li>
	</ul>
</%block>

${next.body()}

