from netprofile.common.modules import ModuleBase
from netprofile.common.menus import Menu
from .models import *

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr

	def add_routes(self, config):
		config.scan()

	def get_css(self, request):
		return [
		]

	def get_js(self, request):
		return [
		]

	def get_models(self):
		return [
			City,
			District,
			Street,
			House,
			Place,
			HGroup
		]

	@property
	def name(self):
		return 'Geo'

