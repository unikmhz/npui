import sys
import cdecimal
sys.modules['decimal'] = cdecimal

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from netprofile.common.modules import ModuleManager
from netprofile.common.factory import RootFactory
from netprofile.db.connection import DBSession

def main(global_config, **settings):
	"""
	This function returns a Pyramid WSGI application.
	"""
	engine = engine_from_config(settings, 'sqlalchemy.')
	DBSession.configure(bind=engine)

	config = Configurator(
		settings=settings,
		root_factory=RootFactory
	)

	return config.make_wsgi_app()

