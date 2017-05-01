## -*- coding: utf-8 -*-
<%inherit file="netprofile_core:templates/base.mak"/>
<%block name="title">${_('Log In') | h}</%block>
<%block name="head_css">
	<link rel="stylesheet" href="${req.static_url('netprofile_core:static/css/login.css')}" type="text/css" media="screen, projection" />
</%block>

<form method="post" action="${req.route_url('core.login')}" ondragstart="return false;" ondrop="return false;">
<div id="login_outer" role="presentation">
	<img alt="NetProfile" src="${req.static_url('netprofile_core:static/img/nplogo.png')}" draggable="false" role="banner" />
	<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf() | h}" />
% if failed:
	<div class="elem errmsg" role="alert">
		${_('Authentication failed.') | h}
	</div>
% endif
	<div class="elem" role="presentation">
		<label id="l_user" for="user" class="x-form-item-label x-form-item-label-default x-unselectable">${_('User Name') | h}</label>
		<div class="x-form-text-wrap x-form-text-wrap-default" role="presentation">
			<input type="text" class="text x-form-field x-form-text x-form-text-default" id="user" name="user" value="" size="28" maxlength="254" tabindex="1" autocomplete="off" aria-labelledby="l_user" required="required" aria-required="true" title="${_('Your password') | h}" />
		</div>
	</div>
	<div class="elem" role="presentation">
		<label id="l_pass" for="pass" class="x-form-item-label x-form-item-label-default x-unselectable">${_('Password') | h}</label>
		<div class="x-form-text-wrap x-form-text-wrap-default" role="presentation">
			<input type="password" class="text x-form-field x-form-text x-form-text-default" id="pass" name="pass" value="" size="28" maxlength="254" tabindex="2" autocomplete="off" aria-labelledby="l_pass" required="required" aria-required="true" title="${_('Your password') | h}" />
		</div>
	</div>
	<div class="elem" role="presentation">
		<label id="l_locale" for="__locale" class="x-form-item-label x-form-item-label-default x-unselectable">${_('Language') | h}</label>
		<select class="text" id="__locale" name="__locale" tabindex="3" class="x-form-field x-form-text x-form-text-default" autocomplete="off" aria-labelledby="l_locale" title="${_('Choose interface language') | h}">
% for lang in req.locales:
			<option label="${'%s [%s]' % (req.locales[lang].english_name, req.locales[lang].display_name) | h}" value="${lang | h}"\
% if lang == cur_loc:
 selected="selected"\
% endif
>${'%s [%s]' % (req.locales[lang].english_name, req.locales[lang].display_name) | h}</option>
% endfor
		</select>
	</div>
	<div class="footer" role="presentation">
		<button type="submit" id="submit" name="submit" title="${_('Log In') | h}" tabindex="4">${_('Log In') | h}</button>
	</div>
</div>
</form>

<script type="text/javascript" src="${req.static_url('netprofile_core:static/js/login.js')}"></script>

