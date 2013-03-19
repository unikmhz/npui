from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from netprofile.common.modules import ModuleBase
from .models import *

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_entities')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_entities:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('geo',)

	def get_models(self):
		return [
			Entity,
			EntityFlag,
			EntityFlagType,
			EntityState,
			PhysicalEntity,
			LegalEntity,
			StructuralEntity,
			ExternalEntity
		]

	def get_css(self, request):
		return [
			'netprofile_entities:static/css/main.css'
		]

	@property
	def name(self):
		return _('Entities')

