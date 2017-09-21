<%!
	bg_color = '#222222'
	footer_color = '#888888'
	block_color = '#ffffff'
	text_color = '#555555'
	heading_color = '#333333'
	spacer_height = '30'
%>\
<!DOCTYPE html>
<html lang="${cur_loc}" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<%def name="mail_block_plain(bgcolor=None)">
			<tr>
				<td bgcolor="${bgcolor or self.attr.block_color}">
${caller.body()}
				</td>
			</tr>
</%def>\
<%def name="mail_block(bgcolor=None)">
			<tr>
				<td bgcolor="${bgcolor or self.attr.block_color}">
					<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
${caller.body()}
					</table>
				</td>
			</tr>
</%def>\
<%def name="mail_onecol(color=None)">
					<tr>
						<td style="padding: 30px; font-family: sans-serif; font-size: 15px; line-height: 20px; color: ${color or self.attr.text_color};">
							<p style="margin: 0 0 10px 0;">
${caller.body()}
							</p>
						</td>
					</tr>
</%def>\
<%def name="mail_heading(color=None, align='left')">
					<tr>
						<td style="padding: 30px 30px 20px; text-align: ${align};">
							<h1 style="margin: 0; font-family: sans-serif; font-size: 24px; line-height: 27px; color: ${color or self.attr.heading_color}; font-weight: normal;">${caller.body()}</h1>
						</td>
					</tr>
</%def>\
<%def name="mail_spacer()">
					<tr>
						<td aria-hidden="true" height="${self.attr.spacer_height}" style="font-size: 0; line-height: 0;">&nbsp;</td>
					</tr>
</%def>\
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="x-apple-disable-message-reformatting">
%if keywords:
	<meta name="keywords" content="${keywords}">
%endif
%if description:
	<meta name="description" content="${description}">
%endif
	<title><%block name="title">${_('Untitled e-mail', domain='netprofile_core')}</%block></title>
	<style>
		html, body { margin: 0 auto !important; padding: 0 !important; height: 100% !important; width: 100% !important; }
		* { -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; }
		div[style*="margin: 16px 0"] { margin: 0 !important; }
		table, td { mso-table-lspace: 0pt !important; mso-table-rspace: 0pt !important; }
		table { border-spacing: 0 !important; border-collapse: collapse !important; table-layout: fixed !important; margin: 0 auto !important; }
		table table table { table-layout: auto; }
		img { -ms-interpolation-mode: bicubic; }
		*[x-apple-data-detectors], .x-gmail-data-detectors, .x-gmail-data-detectors *, .aBn { border-bottom: 0 !important; cursor: default !important; color: inherit !important; text-decoration: none !important; font-size: inherit !important; font-family: inherit !important; font-weight: inherit !important; line-height: inherit !important; }
		.a6S { display: none !important; opacity: 0.01 !important; }
		img.g-img + div { display: none !important; }
		.button-link { text-decoration: none !important; }
		@media only screen and (min-device-width: 375px) and (max-device-width: 413px) {
			.email-container { min-width: 375px !important; }
		}
	</style>
	<style>
		.button-td, .button-a { transition: all 100ms ease-in; }
		.button-td:hover, .button-a:hover { background: ${self.attr.text_color} !important; border-color: ${self.attr.text_color} !important; }
		dl dt { float: left !important; clear: right !important; font-weight: bold !important; }
		dl dd { float: right !important; clear: right !important; }
		@media screen and (max-width: 480px) {
			.fluid { width: 100% !important; max-width: 100% !important; height: auto !important; margin-left: auto !important; margin-right: auto !important; }
			.stack-column, .stack-column-center { display: block !important; width: 100% !important; max-width: 100% !important; direction: ltr !important; }
			.stack-column-center { text-align: center !important; }
			.center-on-narrow { text-align: center !important; display: block !important; margin-left: auto !important; margin-right: auto !important; float: none !important; }
			table.center-on-narrow { display: inline-block !important; }
			.email-container p { font-size: 17px !important; line-height: 22px !important; }
		}
	</style>
	<!--[if gte mso 9]>
	<xml>
		<o:OfficeDocumentSettings>
		<o:AllowPNG/>
		<o:PixelsPerInch>96</o:PixelsPerInch>
		</o:OfficeDocumentSettings>
	</xml>
	<![endif]-->
</head>
<body width="100%" bgcolor="${self.attr.bg_color}" style="margin: 0; mso-line-height-rule: exactly;">
	<center style="width: 100%; background: ${self.attr.bg_color}; text-align: left;">
		<div style="display: none; font-size: 1px; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all; font-family: sans-serif;">
			<%block name="preheader"/>
		</div>
		<div style="max-width: 680px; margin: auto;" class="email-container">
			<!--[if mso]>
			<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="680" align="center">
			<tr><td>
			<![endif]-->
			<table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 680px;" class="email-container">
${next.body()}
			</table>
			<table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 680px; font-family: sans-serif; color: ${self.attr.footer_color}; line-height: 18px;">
			<tr>
				<td style="padding: 30px 10px; width: 100%; font-size: 12px; font-family: sans-serif; line-height: 18px; text-align: center; color: ${self.attr.footer_color};" class="x-gmail-data-detectors">
					<%block name="footer"/>
				</td>
			</tr>
			</table>
			<!--[if mso]>
			</td></tr>
			</table>
			<![endif]-->
		</div>
		<%block name="postfooter"/>
	</center>
</body>
</html>
