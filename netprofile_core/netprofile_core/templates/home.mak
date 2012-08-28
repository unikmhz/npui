<%inherit file="netprofile_core:templates/base.mak"/>
<%block name="head">
  <script type="text/javascript" src="${req.static_url('netprofile_core:static/extjs/ext-all-dev.js')}" charset="UTF-8"></script>
  <script type="text/javascript" src="${req.static_url('netprofile_core:static/extjs/locale/ext-lang-ru.js')}" charset="UTF-8"></script>
  <script type="text/javascript">//<![CDATA[
	Ext.BLANK_IMAGE_URL = '${req.static_url('netprofile_core:static/extjs/resources/themes/images/default/tree/s.gif')}';
  //]]></script>
  <script type="text/javascript" src="${req.route_url('extapi')}" charset="UTF-8"></script>
  <script type="text/javascript" src="${req.route_url('core.js.webshell')}" charset="UTF-8"></script>
</%block>

  <!-- Fields required for history management -->
  <form id="history-form" class="x-hide-display">
    <input type="hidden" id="x-history-field" />
    <iframe id="x-history-frame"></iframe>
  </form>

