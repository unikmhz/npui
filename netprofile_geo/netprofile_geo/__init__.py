from netprofile.common.modules import ModuleBase
from .models import *

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr

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
		return 'Geography'

