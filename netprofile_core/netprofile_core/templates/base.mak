<%namespace name="np" file="netprofile_core:templates/np.mak"/><!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="ru">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge;chrome=1" />
  <meta name="keywords" content="netprofile" />
  <meta name="description" content="NetProfile administrative UI" />
  <title>NetProfile :: <%block name="title">Home</%block></title>
  <link rel="shortcut icon" href="${req.static_url('netprofile_core:static/favicon.ico')}" />
  <link rel="stylesheet" href="${req.static_url('netprofile_core:static/extjs/resources/css/ext-all.css')}" type="text/css" />
  <link rel="stylesheet" href="${req.static_url('netprofile_core:static/css/main.css')}" type="text/css" media="screen, projection" />
<%block name="head"/>
</head>
<body>${self.body()}</body>
</html>

