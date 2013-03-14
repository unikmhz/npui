from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.i18n import (
	TranslationString,
	get_localizer
)

def add_renderer_globals(event):
	request = event['request']
	event['_'] = request.translate
	event['localizer'] = request.localizer

def add_localizer(event):
	request = event.request
	mr = request.matched_route
	if mr is None:
		mr = 'netprofile_core'
	else:
		mr = 'netprofile_' + mr.name.split('.')[0]
	localizer = get_localizer(request)
	def auto_translate(*args, **kwargs):
		kwargs['domain'] = mr
		return localizer.translate(TranslationString(*args, **kwargs))
	request.localizer = localizer
	request.translate = auto_translate

