<%inherit file="netprofile_core:templates/base.mak"/>
<%block name="title">Log In</%block>
<%block name="head">
  <link rel="stylesheet" href="${req.static_url('netprofile_core:static/css/login.css')}" type="text/css" media="screen, projection" />
</%block>

<form method="post" action="${req.route_url('core.login')}">
<div id="login_outer">
  <input type="hidden" id="csrf" name="csrf" value="${req.session.get_csrf_token().decode('utf-8')}" />
    <input type="hidden" name="next" value="${next}" />
% if failed:
  <div class="elem errmsg">
    Authentication failed.
  </div>
% endif
  <div class="elem">
    <label for="user">User name</label><br />
      <input type="text" class="text" id="user" name="user" value="${login}" size="28" maxlength="254" tabindex="1" autocomplete="off" />
  </div>
  <div class="elem">
    <label for="pass">Password</label><br />
    <input type="password" class="text" id="pass" name="pass" value="" size="28" maxlength="254" tabindex="2" autocomplete="off" />
  </div>
  <div class="footer">
    <button type="submit" id="submit" name="submit" title="Log In" tabindex="4">Log In</button>
  </div>
</div>
</form>

