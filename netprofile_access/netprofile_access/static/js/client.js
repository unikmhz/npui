var RecaptchaOptions = {
	tabindex: 9,
	theme:    'white'
};

var _trans = {};
var _ = function(text)
{
	if(text in _trans)
		return _trans[text];
	return text;
};

$(function()
{
	var locale_re = new RegExp('^(.*(?:\\?|&))__locale=([a-zA-Z0-9_.-]+)(.*)$'),
		csrf_token = $('meta[name=csrf-token]').attr('content'),
		trans = $('meta[name=js-translations]').attr('content'),
		file_up = $('#fileupload'),
		dp_onchange = function(ev)
		{
			var me = $(this),
				val = me.find('input[type=text]').val(),
				start_id, end_id, hidden_id;

			if(!ev.date)
				return;
			start_id = me.data('dp-start');
			end_id = me.data('dp-end');
			hidden_id = me.data('dp-hidden');
			if(start_id)
				$('#' + start_id).data('DateTimePicker').setStartDate(ev.date);
			if(end_id)
				$('#' + end_id).data('DateTimePicker').setEndDate(ev.date);
			if(hidden_id)
			{
				if(val)
					$('#' + hidden_id).val(ev.date.format()); // defaults to ISO
				else
					$('#' + hidden_id).val('');
			}
		};

	$.ajaxSetup({
		headers: { 'X-CSRFToken': csrf_token }
	});
	if(trans)
		_trans = $.parseJSON(trans);
	$('input,select,textarea').not('[type=submit],#__locale').jqBootstrapValidation({
		preventSubmit: true
	});
	$('.chosen-select').chosen({
		search_contains: true
	});
	$('.dt-picker').datetimepicker({
		language: $('html').attr('lang')
	}).on('change.dp', dp_onchange).each(function(i, dp)
	{
		var dp = $(dp),
			val = dp.find('input[type=hidden]').val(),
			dpw = dp.data('DateTimePicker'),
			start_id = dp.data('dp-start'),
			end_id = dp.data('dp-end');

		if(!val)
			return;
		dpw.setDate(val);
		if(start_id)
			$('#' + start_id).data('DateTimePicker').setStartDate(dpw.getDate());
		if(end_id)
			$('#' + end_id).data('DateTimePicker').setEndDate(dpw.getDate());
	});
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
	if(file_up.length)
	{
		file_up.fileupload({
			url: '/upload',
			dataType: 'json',
			filesContainer: $('tbody.files'),
			uploadTemplateId: null,
			downloadTemplateId: null,
			uploadTemplate: function(o)
			{
		        var rows = $();

				$.each(o.files, function(i, file)
				{
					var node, td;

					node = $('<tr class="template-upload fade"/>')
						.append($('<td/>').append([
							$('<p class="name"/>').text(file.name),
							$('<strong class="error text-danger"/>')
						]))
						.append($('<td/>').append([
							$('<p class="size"/>').text(_('Processing…')),
							$('<div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"/>')
								.append($('<div class="progress-bar progress-bar-success" style="width:0%;"/>'))
						]));
					td = $('<td/>');
					if(!i && !o.options.autoUpload)
						td.append([
							$('<button class="btn btn-primary start" disabled="disabled"/>')
								.text(' ' + _('Begin'))
								.prepend($('<span class="glyphicon glyphicon-upload"/>')),
							'&nbsp;'
						]);
					if(!i)
						td.append($('<button class="btn btn-warning cancel"/>')
							.text(' ' + _('Cancel'))
							.prepend($('<span class="glyphicon glyphicon-ban-circle"/>'))
						);
					node.append(td);
					rows = rows.add(node);
				});
				return rows;
			},
			downloadTemplate: function(o)
			{
				var rows = $();

				$.each(o.files, function(i, file)
				{
					var node, td, el, el2;

					node = $('<tr class="template-download fade"/>');
					el = $('<p class="name"/>');
					if(file.url)
					{
						el.append(el2 = $('<a/>')
							.text(file.name)
							.attr({
								'href'     : file.url,
								'title'    : file.name,
								'download' : file.name
							})
						);
						if(file.thumbnailUrl)
							el2.attr('data-gallery', 'data-gallery');
					}
					else
						el.append($('<span/>').text(file.name));
					td = $('<td/>').append(el);
					if(file.error)
						td.append($('<div/>').text(file.error).prepend(
							$('<span class="label label-danger"/>').text(_('Error'))
						));
					node.append(td);
					node.append($('<td/>').append(
						$('<span class="size"/>').text(o.formatFileSize(file.size))
					));
					td = $('<td/>');
					if(file.deleteUrl)
					{
						td.append(el = $('<button class="btn btn-danger delete"/>')
							.attr({
								'data-type' : file.deleteType,
								'data-url'  : file.deleteUrl
							})
							.text(' ' + _('Delete'))
							.prepend($('<span class="glyphicon glyphicon-trash"/>'))
						);
						if(file.deleteWithCredentials)
							el.attr('data-xhr-fields', '{"withCredentials":true}');
						td.append($('<input type="checkbox" name="delete" value="1" class="toggle pull-right"/>'));
					}
					else
					{
						td.append($('<button class="btn btn-warning cancel"/>')
							.text(' ' + _('Cancel'))
							.prepend($('<span class="glyphicon glyphicon-ban-circle"/>'))
						);
					}
					node.append(td);
					rows = rows.add(node);
				});
				return rows;
			}
		}).addClass('fileupload-processing');

		$.ajax({
			url: file_up.fileupload('option', 'url'),
			method: 'GET',
			data: file_up.serialize(),
			dataType: 'json',
			context: file_up[0]
		}).always(function()
		{
			$(this).removeClass('fileupload-processing');
		}).done(function(result)
		{
			$(this).fileupload('option', 'done')
				.call(this, $.Event('done'), {result: result});
		});
	}
});

