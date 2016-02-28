## -*- coding: utf-8 -*-
<%inherit file="netprofile_core:templates/base.mak"/>
<%block name="title">${_('Access Denied', domain='netprofile_core') | h}</%block>\
<%block name="head_css">\
	<link rel="stylesheet" href="${req.static_url('netprofile_core:static/css/login.css')}" type="text/css" media="screen, projection" />\
</%block>\
<div id="login_outer" role="presentation">
	<img alt="NetProfile" src="${req.static_url('netprofile_core:static/img/nplogo.png')}" draggable="false" role="banner" />
	<div class="elem errheader">
		${_('Error %d', domain='netprofile_core') % (403,) | h}
	</div>
	<div class="elem errbody">${_('Resource access was forbidden.', domain='netprofile_core') | h}</div>
</div>

