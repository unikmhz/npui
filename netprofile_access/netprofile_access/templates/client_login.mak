## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>
<%block name="title">${_('Log In')}</%block>
<%block name="head">\
	<script type="text/javascript" src="${req.static_url('netprofile_access:static/js/login.js')}"></script>\
</%block>

<form method="post" action="${req.route_url('access.cl.login')}">
<div id="login_outer"><div id="login">
	<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
% if failed:
	<div class="errmsg">${_('Authentication failed.')}</div>
% endif
	<div class="elem">
		<label for="user">${_('User Name')}</label>
		<div class="wrap"><input class="text" type="text" id="user" name="user" title="${_('Enter your user name here')}" value="" size="28" maxlength="254" tabindex="1" autocomplete="off" /></div>
	</div>
	<div class="elem">
		<label for="pass">${_('Password')}</label>
		<div class="wrap"><input class="text" type="password" id="pass" name="pass" title="${_('Enter your password here')}" value="" size="28" maxlength="254" tabindex="2" autocomplete="off" /></div>
	</div>
	<div class="elem">
		<label for="__locale">${_('Language')}</label>
		<div class="wrap"><select class="text" id="__locale" name="__locale" tabindex="3" autocomplete="off">
% for lang in langs:
			<option label="${lang[1]}" value="${lang[0]}"\
% if lang[0] == cur_loc:
 selected="selected"\
% endif
>${lang[1]}</option>
% endfor
		</select></div>
	</div>
	<div id="buttons">
		<button type="submit" id="submit" name="submit" title="${_('Log in to your account')}" tabindex="4">${_('Log In')}</button>
% if can_reg:
		<button type="submit" id="register" name="register" class="side" title="${_('Register new account')}" tabindex="5">${_('Register')}</button>
% endif
% if can_recover:
		<button type="submit" id="recover" name="recover" class="side" title="${_('Recover lost password via e-mail')}" tabindex="6">${_('Lost Password?')}</button>
% endif
	</div>
</div></div>
</form>

