class Menu(object):
	def __init__(self, name, title=None, order=10, permission=None):
		self.name = name
		if title is None:
			self.title = name
		else:
			self.title = title
		self.order = order
		self.perm = permission

	def json_repr(self):
		ret = {
			'name'  : self.name,
			'title' : self.title,
			'order' : self.order
		}
		if self.perm is not None:
			ret['perm'] = self.perm
		return ret

