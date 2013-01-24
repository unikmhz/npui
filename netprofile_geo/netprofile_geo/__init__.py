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

	@property
	def name(self):
		return _('Geography')

