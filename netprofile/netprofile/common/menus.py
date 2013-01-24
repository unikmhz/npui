from pyramid.threadlocal import get_current_request
from pyramid.i18n import (
	TranslationString,
	get_localizer
)

class Menu(object):
	"""
	Defines a single menu pane on the left side of the UI.
	"""
	def __init__(self, name, **kwargs):
		self.name = name
		self.title = kwargs.get('title', name)
		self.order = kwargs.get('order', 10)
		self.perm = kwargs.get('permission')
		self.direct = kwargs.get('direct')
		self.url = kwargs.get('url')

	def json_repr(self):
		ttl = self.title
		if isinstance(ttl, TranslationString):
			req = get_current_request()
			if req is not None:
				loc = get_localizer(req)
				ttl = loc.translate(ttl)
		ret = {
			'name'   : self.name,
			'title'  : ttl,
			'order'  : self.order,
			'direct' : self.direct,
			'url'    : self.url
		}
		if self.perm is not None:
			ret['perm'] = self.perm
		return ret

