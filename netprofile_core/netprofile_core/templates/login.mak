## -*- coding: utf-8 -*-
<%inherit file="netprofile_core:templates/base.mak"/>
<%block name="title">${_('Log In')}</%block>
<%block name="head">
	<link rel="stylesheet" href="${req.static_url('netprofile_core:static/css/login.css')}" type="text/css" media="screen, projection" />
</%block>

<form method="post" action="${req.route_url('core.login')}">
<div id="login_outer">
	<img alt="NetProfile" src="${req.static_url('netprofile_core:static/img/nplogo.png')}" />
	<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
	<input type="hidden" name="next" value="${next}" />
% if failed:
	<div class="elem errmsg">
		${_('Authentication failed.')}
	</div>
% endif
	<div class="elem">
		<label for="user" class="x-form-item-label x-form-item-label-default x-unselectable">${_('User Name')}</label>
		<div class="x-form-text-wrap x-form-text-wrap-default">
			<input type="text" class="text x-form-field x-form-text x-form-text-default" id="user" name="user" value="" size="28" maxlength="254" tabindex="1" autocomplete="off" />
		</div>
	</div>
	<div class="elem">
		<label for="pass" class="x-form-item-label x-form-item-label-default x-unselectable">${_('Password')}</label>
		<div class="x-form-text-wrap x-form-text-wrap-default">
			<input type="password" class="text x-form-field x-form-text x-form-text-default" id="pass" name="pass" value="" size="28" maxlength="254" tabindex="2" autocomplete="off" />
		</div>
	</div>
	<div class="elem">
		<label for="__locale" class="x-form-item-label x-form-item-label-default x-unselectable">${_('Language')}</label>
		<select class="text" id="__locale" name="__locale" tabindex="3" class="x-form-field x-form-text x-form-text-default" autocomplete="off">
% for lang in req.locales:
			<option label="${'%s [%s]' % (req.locales[lang].english_name, req.locales[lang].display_name)}" value="${lang}"\
% if lang == cur_loc:
 selected="selected"\
% endif
>${'%s [%s]' % (req.locales[lang].english_name, req.locales[lang].display_name)}</option>
% endfor
		</select>
	</div>
	<div class="footer">
		<button type="submit" id="submit" name="submit" title="Log In" tabindex="4">${_('Log In')}</button>
	</div>
</div>
</form>

<script type="text/javascript">
	var fld;

	fld = document.getElementById('user');
	if(fld)
	{
		fld.value = '';
		fld.focus();
	}

	fld = document.getElementById('pass');
	if(fld)
		fld.value = '';

	function on_change_lang()
	{
		var f, q, re;

		f = document.getElementById('user');
		if(f.value === '')
		{
			f = document.getElementById('__locale');
			if(f)
			{
				q = window.location.search;
				if(q)
				{
					re = /__locale=[\w_-]+/;
					if(q.match(re))
						q = q.replace(re, '__locale=' + f.value);
					else
						q += '&__locale=' + f.value;
				}
				else
					q = '?__locale=' + f.value;
				window.location.search = q;
			}
		}
		return false;
	}

	fld = document.getElementById('__locale');
	if(fld)
		fld.onchange = on_change_lang;
</script>

