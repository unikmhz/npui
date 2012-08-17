from netprofile.common.modules import ModuleBase
from netprofile.common.menus import Menu
from .models import *

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_route('core.home', '/')
		mmgr.cfg.add_route('core.login', '/login')
		mmgr.cfg.add_route('core.logout', '/logout')

	def add_routes(self, config):
		config.add_route('core.js.webshell', '/js/webshell')
		config.scan()

	def get_models(self):
		return [
			NPModule,
			User,
			Group,
			Privilege,
			UserCapability,
			GroupCapability,
			UserACL,
			GroupACL,
			UserGroup,
			SecurityPolicy,
			FileFolder,
			File,
			Tag,
			LogType,
			LogAction,
			LogData,
			NPSession,
			PasswordHistory,
			GlobalSettingSection,
			UserSettingSection,
			GlobalSetting,
			UserSettingType,
			UserSetting
		]

	def get_menus(self):
		return [
			Menu('modules', title='Modules', order=10),
			Menu('settings', title='Settings', order=20),
			Menu('admin', title='Administration', order=30, permission='BASE_ADMIN')
		]

	def get_css(self):
		return [
			'netprofile.modules.core:static/extjs/resources/css/ext-all.css',
			'netprofile.modules.core:static/css/main.css'
		]

	@property
	def name(self):
		return 'Core'

