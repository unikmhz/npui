from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from netprofile.common.modules import ModuleBase
from .models import *

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_geo')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_geo:locale/')
		mmgr.cfg.scan()

	def get_models(self):
		return [
			City,
			District,
			Street,
			House,
			Place,
			HouseGroup,
			HouseGroupMapping
		]

	def get_local_js(self, request, lang):
		return [
			'netprofile_geo:static/webshell/locale/webshell-lang-' + lang + '.js'
		]

	def get_autoload_js(self, request):
		return [
			'NetProfile.geo.form.field.Address'
		]

	@property
	def name(self):
		return _('Geography')

