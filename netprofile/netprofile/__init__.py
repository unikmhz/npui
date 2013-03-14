from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import sys
import cdecimal
sys.modules['decimal'] = cdecimal

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from netprofile.common.modules import IModuleManager
from netprofile.common.factory import RootFactory
from netprofile.db.connection import DBSession

LANGUAGES = [
	('en', 'English (US)'),
	('ru', 'Russian [Русский]')
]

LANG_MAP = {
	'en'      : 'en',
	'eng'     : 'en',
	'english' : 'en',
	'en-US'   : 'en',
	'en_US'   : 'en',
	'ru'      : 'ru',
	'rus'     : 'ru',
	'russian' : 'ru',
	'ru-RU'   : 'ru',
	'ru_RU'   : 'ru'
}

def locale_neg(request):
	avail = request.registry.settings.get('pyramid.available_languages', '').split()
	loc = request.params.get('__locale')
	if loc is None:
		loc = request.session.get('ui.locale')
	if loc is None and request.accept_language:
		loc = request.accept_language.best_match(LANG_MAP)
		loc = LANG_MAP.get(loc)
	if loc is None:
		loc = request.registry.settings.get('pyramid.default_locale_name', 'en')
	if loc in avail:
		request.session['ui.locale'] = loc
		return loc
	return 'en'

def main(global_config, **settings):
	"""
	This function returns a Pyramid WSGI application.
	"""
	engine = engine_from_config(settings, 'sqlalchemy.')
	DBSession.configure(bind=engine)

	config = Configurator(
		settings=settings,
		root_factory=RootFactory,
		locale_negotiator=locale_neg
	)

	config.add_subscriber(
		'netprofile.common.subscribers.add_renderer_globals',
		'pyramid.events.BeforeRender'
	)
	config.add_subscriber(
		'netprofile.common.subscribers.add_localizer',
		'pyramid.events.NewRequest'
	)

	mmgr = config.registry.getUtility(IModuleManager)
	mmgr.load('core')
	mmgr.load_enabled()

	return config.make_wsgi_app()

