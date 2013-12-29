var RecaptchaOptions = {
	tabindex: 9,
	theme:    'clean'
};

$(function()
{
	var locale_re = new RegExp('^(.*(?:\\?|&))__locale=([a-zA-Z0-9_.-]+)(.*)$'),
		csrf_token = $('meta[name=csrf-token]').attr('content');

	$.ajaxSetup({
		headers: { 'X-CSRFToken': csrf_token }
	});
	$('input,select,textarea').not('[type=submit],#__locale').jqBootstrapValidation({
		preventSubmit: true
	});
	$('.chosen-select').chosen();
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
