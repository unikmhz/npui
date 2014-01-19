var RecaptchaOptions = {
	tabindex: 9,
	theme:    'white'
};

$(function()
{
	var locale_re = new RegExp('^(.*(?:\\?|&))__locale=([a-zA-Z0-9_.-]+)(.*)$'),
		csrf_token = $('meta[name=csrf-token]').attr('content'),
		file_up = $('#fileupload');

	$.ajaxSetup({
		headers: { 'X-CSRFToken': csrf_token }
	});
	$('input,select,textarea').not('[type=submit],#__locale').jqBootstrapValidation({
		preventSubmit: true
	});
	$('.chosen-select').chosen();
	$('.no-js').removeClass('no-js');
	$('.hide-no-js').removeClass('hide-no-js');
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
//						.append($('<td/>').append($('<span class="preview"/>')))
						.append($('<td/>').append([
							$('<p class="name"/>').text(file.name),
							$('<strong class="error text-danger"/>')
						]))
						.append($('<td/>').append([
							$('<p class="size"/>').text('Processing...'),
							$('<div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"/>')
								.append($('<div class="progress-bar progress-bar-success" style="width:0%;"/>'))
						]));
					td = $('<td/>');
					if(!i && !o.options.autoUpload)
						td.append([
							$('<button class="btn btn-primary start" disabled="disabled"/>')
								.text(' Start')
								.prepend($('<span class="glyphicon glyphicon-upload"/>')),
							'&nbsp;'
						]);
					if(!i)
						td.append($('<button class="btn btn-warning cancel"/>')
							.text(' Cancel')
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
//					el = $('<span class="preview"/>');
//					if(file.thumbnailUrl)
//						el.append($('<a/>')
//							.attr({
//								'href'         : file.url,
//								'title'        : file.name,
//								'download'     : file.name,
//								'data-gallery' : 'data-gallery'
//							})
//							.append($('<img/>').attr('src', file.thumbnailUrl))
//						);
//					node.append($('<td/>').append(el));
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
							$('<span class="label label-danger"/>').text('Error')
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
							.text(' Delete')
							.prepend($('<span class="glyphicon glyphicon-trash"/>'))
						);
						if(file.deleteWithCredentials)
							el.attr('data-xhr-fields', '{"withCredentials":true}');
						td.append($('<input type="checkbox" name="delete" value="1" class="toggle pull-right"/>'));
					}
					else
					{
						td.append($('<button class="btn btn-warning cancel"/>')
							.text(' Cancel')
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

