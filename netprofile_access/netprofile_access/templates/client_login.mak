## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>
<%block name="title">${_('Log In')}</%block>

<form method="post" action="${req.route_url('access.cl.login')}">
<div id="login_outer"><div id="login">
	<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
% if failed:
	<div class="errmsg">${_('Authentication failed.')}</div>
% endif
	<div class="elem">
		<label for="user">${_('User Name')}</label>
		<div class="wrap"><input class="text" type="text" id="user" name="user" value="" size="28" maxlength="254" tabindex="1" autocomplete="off" /></div>
	</div>
	<div class="elem">
		<label for="pass">${_('Password')}</label>
		<div class="wrap"><input class="text" type="password" id="pass" name="pass" value="" size="28" maxlength="254" tabindex="2" autocomplete="off" /></div>
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
		<button type="submit" id="submit" name="submit" title="Log In" tabindex="4">${_('Log In')}</button>
	</div>
</div></div>
</form>

