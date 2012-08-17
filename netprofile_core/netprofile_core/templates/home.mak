<%inherit file="netprofile_core:templates/base.mak"/>
<%block name="head">
  <script type="text/javascript" src="${request.route_url('extapi')}" charset="UTF-8"></script>
  <script type="text/javascript" src="${request.route_url('core.js.webshell')}" charset="UTF-8"></script>
</%block>

  <!-- Fields required for history management -->
  <form id="history-form" class="x-hide-display">
    <input type="hidden" id="x-history-field" />
    <iframe id="x-history-frame"></iframe>
  </form>

