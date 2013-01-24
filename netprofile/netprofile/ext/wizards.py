from netprofile.ext.data import ExtRelationshipColumn

class Step(object):
	def __init__(self, *args, **kwargs):
		self.fields = args
		self.title = kwargs.get('title')
		self.id = kwargs.get('id')
		self.validate = kwargs.get('validate', True)

	def get_cfg(self, model, req, **kwargs):
		step = []
		for field in self.fields:
			col = model.get_column(field)
			colfld = col.get_editor_cfg(req, in_form=True)
			if colfld:
				coldef = col.default
				if (kwargs.get('use_defaults', False)) and (coldef is not None):
					colfld['value'] = coldef
				step.append(colfld)
				if isinstance(col, ExtRelationshipColumn) and ('hiddenField' in colfld):
					hcol = model.get_column(colfld['hiddenField'])
					colfld = hcol.get_editor_cfg(req, in_form=True)
					coldef = hcol.default
					if (kwargs.get('use_defaults', False)) and (coldef is not None):
						colfld['value'] = coldef
					step.append(colfld)
		cfg = {
			'xtype' : 'npwizardpane',
			'items' : step,
			'doValidation' : self.validate
		}
		if self.title:
			cfg['title'] = self.title
		return cfg

class Wizard(object):
	def __init__(self, *args, **kwargs):
		self.steps = args
		self.title = kwargs.get('title')

	def get_cfg(self, model, req, **kwargs):
		res = []
		idx = 0
		for step in self.steps:
			if step.id is None:
				step.id = 'step' + str(idx)
			scfg = step.get_cfg(model, req, **kwargs)
			if scfg:
				scfg['itemId'] = step.id
				res.append(scfg)
				idx += 1
		return res

class SimpleWizard(Wizard):
	def get_cfg(self, model, req, **kwargs):
		step = []
		for cname, col in model.get_read_columns().items():
			colfld = col.get_editor_cfg(req, in_form=True)
			if colfld:
				coldef = col.default
				if coldef is not None:
					colfld['value'] = coldef
					if isinstance(col, ExtRelationshipColumn) and ('hiddenField' in colfld):
						hdval = col.get_related_by_value(coldef)
						if hdval:
							colfld['value'] = str(hdval)
				step.append(colfld)
		return [{
			'itemId'       : 'step0',
			'xtype'        : 'npwizardpane',
			'items'        : step,
			'doValidation' : True
		}]

