## -*- coding: utf-8 -*-
<%inherit file="netprofile_core:templates/base.mak"/>
<%block name="title">Log In</%block>
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
		<label for="user">${_('User Name')}</label><br />
		<input type="text" class="text" id="user" name="user" value="" size="28" maxlength="254" tabindex="1" style="width: 100%;" autocomplete="off" />
	</div>
	<div class="elem">
		<label for="pass">${_('Password')}</label><br />
		<input type="password" class="text" id="pass" name="pass" value="" size="28" maxlength="254" tabindex="2" style="width: 100%;" autocomplete="off" />
	</div>
	<div class="elem">
		<label for="__locale">${_('Language')}</label><br />
		<select class="text" id="__locale" name="__locale" tabindex="3" style="width: 100%;" autocomplete="off">
% for lang in langs:
			<option label="${lang[1]}" value="${lang[0]}"\
% if lang[0] == cur_loc:
 selected="selected"\
% endif
>${lang[1]}</option>
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

