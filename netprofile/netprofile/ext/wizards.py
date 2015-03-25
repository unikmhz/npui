#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Classes used to produce UI wizards
# © Copyright 2013-2015 Alex 'Unik' Unigovsky
#
# This file is part of NetProfile.
# NetProfile is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later
# version.
#
# NetProfile is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General
# Public License along with NetProfile. If not, see
# <http://www.gnu.org/licenses/>.

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.i18n import get_localizer

from netprofile.db.fields import EnumMeta
from netprofile.ext.data import (
	_name_to_class,
	ExtModel,
	ExtRelationshipColumn
)

def _add_field(step, model, req, field, **kwargs):
	if isinstance(field, CustomWizardField):
		fcfg = field.get_cfg(model, req, **kwargs)
		if fcfg is not None:
			if (not kwargs.get('use_defaults', False)) and ('value' in fcfg):
				del fcfg['value']
			if isinstance(fcfg, list):
				step.extend(fcfg)
			else:
				step.append(fcfg)
		return
	col = model.get_column(field)
	colfld = col.get_editor_cfg(req, in_form=True)
	if colfld:
		coldef = col.default
		if (kwargs.get('use_defaults', False)) and (coldef is not None):
			colfld['value'] = coldef
			if isinstance(col, ExtRelationshipColumn) and ('hiddenField' in colfld):
				hdval = col.get_related_by_value(coldef)
				if hdval:
					colfld['value'] = str(hdval)
		step.append(colfld)
		if isinstance(col, ExtRelationshipColumn) and ('hiddenField' in colfld):
			hcol = model.get_column(colfld['hiddenField'])
			colfld = hcol.get_editor_cfg(req, in_form=True)
			coldef = hcol.default
			if (kwargs.get('use_defaults', False)) and (coldef is not None):
				colfld['value'] = coldef
			step.append(colfld)

class CustomWizardField(object):
	"""
	Non-standard wizard field.
	"""
	def get_cfg(self, model, req, **kwargs):
		return None

class ExtJSWizardField(CustomWizardField):
	"""
	Wizard field containing arbitrary ExtJS configuration.
	"""
	def __init__(self, cfg):
		self.cfg = cfg

	def get_cfg(self, model, req, **kwargs):
		if callable(self.cfg):
			return self.cfg(self, model, req, **kwargs)
		return self.cfg

class DeclEnumWizardField(CustomWizardField):
	"""
	Combo box field; auto-created from a DeclEnum.
	"""
	def __init__(self, name, enum, **kwargs):
		assert isinstance(enum, EnumMeta), \
			'Tried to generate a wizard field from something othen than an enum.'
		self.name = name
		self.enum = enum
		self.kw = kwargs

	def get_cfg(self, model, req, **kwargs):
		loc = get_localizer(req)
		store = []
		maxlen = 0
		for sym in self.enum:
			store.append({
				'id'    : sym.value,
				'value' : loc.translate(sym.description)
			})
		return {
			'xtype'          : 'combobox',
			'allowBlank'     : self.kw.get('nullable', False),
			'name'           : self.name,
			'fieldLabel'     : loc.translate(self.kw.get('label', self.name)),
			'format'         : 'string',
			'displayField'   : 'value',
			'valueField'     : 'id',
			'queryMode'      : 'local',
			'editable'       : False,
			'forceSelection' : True,
			'store'          : {
				'xtype'  : 'simplestore',
				'fields' : ('id', 'value'),
				'data'   : store
			}
		}

class CompositeWizardField(CustomWizardField):
	"""
	Custom wizard field that is composed of several other fields.
	"""
	def __init__(self, *fields, **kwargs):
		self.fields = fields

	def get_cfg(self, model, req, **kwargs):
		items = []
		for f in self.fields:
			_add_field(items, model, req, f, **kwargs)
		return {
			'xtype'  : 'panel',
			'layout' : 'hbox',
			'items'  : items,
			'border' : 0
		}

class ExternalWizardField(CustomWizardField):
	"""
	Generates wizard fields from arbitrary models.
	"""
	def __init__(self, cls, fldname, name=None, value=None, extra_config=None):
		if name is None:
			name = fldname
		self.name = name
		self.model = cls
		self.field = fldname
		self.value = value
		self.extra_config = extra_config

	def get_cfg(self, model, req, **kwargs):
		if isinstance(self.model, str):
			self.model = ExtModel(_name_to_class(self.model))
		ret = []
		col = self.model.get_column(self.field)
		colfld = col.get_editor_cfg(req, in_form=True, initval=self.value)
		if colfld:
			colfld['name'] = self.name
			coldef = col.default
			if (kwargs.get('use_defaults', False)) and (coldef is not None) and (not self.value):
				colfld['value'] = coldef
			if self.extra_config:
				colfld.update(self.extra_config)
			ret = [colfld]
			extra = col.append_field()
			while extra:
				ecol = self.model.get_column(extra)
				ecolfld = ecol.get_editor_cfg(req, in_form=True, initval=self.value)
				if ecolfld:
					ecoldef = ecol.default
					if (kwargs.get('use_defaults', False)) and (ecoldef is not None) and (not self.value):
						ecolfld['value'] = ecoldef
					ret.append(ecolfld)
					extra = ecol.append_field()
				else:
					break
			return ret

class Step(object):
	"""
	Single pane of a wizard. Wizards always contain at least one of these.
	"""
	def __init__(self, *args, **kwargs):
		self.fields = list(args)
		self.title = kwargs.get('title')
		self.id = kwargs.get('id')
		self.validate = kwargs.get('validate', True)
		self.on_next = kwargs.get('on_next')
		self.on_prev = kwargs.get('on_prev')
		self.on_submit = kwargs.get('on_submit', False)

	def get_cfg(self, model, req, **kwargs):
		step = []
		loc = get_localizer(req)
		for field in self.fields:
			if isinstance(field, CustomWizardField):
				fcfg = field.get_cfg(model, req, **kwargs)
				if fcfg is not None:
					if (not kwargs.get('use_defaults', False)) and ('value' in fcfg):
						del fcfg['value']
					if isinstance(fcfg, list):
						step.extend(fcfg)
					else:
						step.append(fcfg)
				continue
			col = model.get_column(field)
			colfld = col.get_editor_cfg(req, in_form=True)
			if colfld:
				coldef = col.default
				if (kwargs.get('use_defaults', False)) and (coldef is not None):
					colfld['value'] = coldef
					if isinstance(col, ExtRelationshipColumn) and ('hiddenField' in colfld):
						hdval = col.get_related_by_value(coldef)
						if hdval:
							colfld['value'] = str(hdval)
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
			cfg['title'] = loc.translate(self.title)
		if self.on_prev:
			if callable(self.on_prev):
				cfg['remotePrev'] = True
			else:
				cfg['remotePrev'] = self.on_prev
		if self.on_next:
			if callable(self.on_next):
				cfg['remoteNext'] = True
			else:
				cfg['remoteNext'] = self.on_next
		if self.on_submit:
			cfg['allowSubmit'] = True
		return cfg

class Wizard(object):
	"""
	Generic wizard object. Generally viewed client-side on 'create' and other events.
	"""
	def __init__(self, *args, **kwargs):
		self.init_done = False
		self.steps = list(args)
		self.title = kwargs.get('title')
		self.validator = kwargs.get('validator')

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
		req.run_hook(
			'np.wizard.cfg.%s.%s' % (model.model.__moddef__, model.model.__name__),
			self, model, res
		)
		return res

	def action(self, model, step_id, act, values, req):
		step = None
		for xstep in self.steps:
			if xstep.id == step_id:
				step = xstep
				break
		if step:
			cb = None
			if act == 'prev':
				cb = step.on_prev
			elif act == 'next':
				cb = step.on_next
			elif act == 'submit':
				cb = step.on_submit
			if cb:
				if callable(cb):
					return cb(self, model, step, act, values, req)
				return { 'do' : 'goto', 'goto' : cb }

class SimpleWizard(Wizard):
	"""
	Single-pane wizard which mimics model's edit form.
	"""
	def get_cfg(self, model, req, **kwargs):
		step = []
		for cname, col in model.get_form_columns().items():
			if col.get_read_only(req):
				continue
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
		res = [{
			'itemId'       : 'step0',
			'xtype'        : 'npwizardpane',
			'items'        : step,
			'doValidation' : True
		}]
		req.run_hook(
			'np.wizard.cfg.%s.%s' % (model.model.__moddef__, model.model.__name__),
			self, model, res
		)
		return res

