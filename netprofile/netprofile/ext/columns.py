from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

class PseudoColumn(object):
	def __init__(self, **kwargs):
		self.nullable = bool(kwargs.get('nullable', True))
		self.template = kwargs.get('template', None)
		self.column_xtype = kwargs.get('column_xtype', None)
		self.editor_xtype = kwargs.get('editor_xtype', 'textfield')
		self.js_type = kwargs.get('js_type', 'auto')
		self.header_string = kwargs.get('header_string', self.name)
		self.column_name = kwargs.get('column_name', self.header_string)
		self.help_text = kwargs.get('help_text', None)
		self.column_width = kwargs.get('column_width', None)
		self.column_resizable = bool(kwargs.get('column_resizable', True))
		self.cell_class = kwargs.get('cell_class', None)
		self.filter_type = kwargs.get('filter_type', 'none')
		self.pass_request = bool(kwargs.get('pass_request', False))
		self.secret_value = bool(kwargs.get('secret_value', False))

class HybridColumn(PseudoColumn):
	def __init__(self, pname, **kwargs):
		self.name = pname
		super(HybridColumn, self).__init__(**kwargs)

class MarkupColumn(PseudoColumn):
	def __init__(self, **kwargs):
		self.name = kwargs.get('name')
		super(MarkupColumn, self).__init__(**kwargs)

