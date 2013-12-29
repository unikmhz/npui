## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>
<%block name="title">${_('Register')}</%block>
<%block name="menubar">
				<ul class="nav navbar-nav">
					<li><a href="${req.route_url('access.cl.login')}" title="${_('Go back to login page')}">${_('Already Registered')}</a></li>
				</ul>
</%block>

${next.body()}

