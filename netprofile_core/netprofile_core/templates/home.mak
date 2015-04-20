## -*- coding: utf-8 -*-
<%inherit file="netprofile_core:templates/base.mak"/>
<%block name="head">
	<script type="text/javascript" src="${req.route_url('extapi')}" charset="UTF-8"></script>
	<script type="text/javascript" src="${req.route_url('core.js.webshell')}" charset="UTF-8"></script>
</%block>

	<!-- Fields required for b/c history management -->
	<form id="history-form" class="x-hidden-display">
		<input type="hidden" id="x-history-field" />
		<iframe id="x-history-frame"></iframe>
	</form>

	<div id="splash"><div class="splashcont">
		<img src="${req.static_url('netprofile_core:static/img/loading-bars.svg')}" alt="${_('Please wait while the application is loading…') | h}" />
		<h1>${_('Loading…') | h}</h1>
	</div></div>

