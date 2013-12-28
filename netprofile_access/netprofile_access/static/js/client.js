var RecaptchaOptions = {
	theme: 'clean',
	tabindex: 9
};

$(function()
{
	var locale_re = new RegExp('^(.*(?:\\?|&))__locale=([a-zA-Z0-9_.-]+)(.*)$');

	$('#__locale').change(function()
	{
		var lang = $(this).val(),
			sstr = window.location.search,
			m;

		if($('#user').val())
			return false;
		if(sstr)
		{
			if(m = locale_re.exec(sstr))
				window.location.search = m[1] + '__locale=' + lang + m[3];
			else
				window.location.search += '&__locale=' + lang;
		}
		else
			window.location.search = '?__locale=' + lang;
		return false;
	});
});
