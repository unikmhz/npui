<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" xmlns:tal="http://xml.zope.org/namespaces/tal">
<head>
  <title>Password reminder</title>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
  <meta name="keywords" content="python web application" />
  <meta name="description" content="pyramid web application" />
  <link rel="shortcut icon" href="${request.static_url('netprofile_useraccount:static/favicon.ico')}" />
  <link rel="stylesheet" href="${request.static_url('netprofile_useraccount:static/pylons.css')}" type="text/css" media="screen" charset="utf-8" />
  <link rel="stylesheet" href="http://static.pylonsproject.org/fonts/nobile/stylesheet.css" media="screen" />
  <link rel="stylesheet" href="http://static.pylonsproject.org/fonts/neuton/stylesheet.css" media="screen" />
</head>
<body>
  <div id="wrap">
    <div id="middle">
      <div class="middle align-center">
          % if not back:
          ${message}
          <form action="/forgotpassword" method="POST"><br>
              <input type="text" name="username">Username</input><br>
              <input type="submit" value='Remind'>
          </form>
          % else:
              ${back|n}
                ${message}<br>
          % endif
    </div>
</body>
</html>
