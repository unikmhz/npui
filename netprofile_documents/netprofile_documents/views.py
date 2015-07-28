#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Documents module - Views
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

from pyramid.view import (
	view_config
)
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)
from pyramid.security import has_permission
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession
from netprofile.ext.direct import extdirect_method

from .models import (
	Document,
	DocumentType
)

_ = TranslationStringFactory('netprofile_documents')

@register_hook('core.dpanetabs.documents.DocumentBundle')
def _dpane_docbundle_documents(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Contents')),
		'iconCls'           : 'ico-mod-document',
		'xtype'             : 'grid_documents_DocumentBundleMapping',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('bundle',),
		'extraParamProp'    : 'dbid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpane.entities.Entity')
@register_hook('core.dpane.entities.PhysicalEntity')
@register_hook('core.dpane.entities.LegalEntity')
@register_hook('core.dpane.entities.StructuralEntity')
@register_hook('core.dpane.entities.ExternalEntity')
@register_hook('core.dpane.entities.AccessEntity')
def _dpane_make_doc(cont, model, req):
	if not has_permission('DOCUMENTS_GENERATE', req.context, req):
		return
	loc = get_localizer(req)
	button = {
		'text'    : loc.translate(_('Documents')),
		'iconCls' : 'ico-print',
		'itemId'  : 'btn_documents',
		'menu'    : {
			'xtype'         : 'menu',
			'plain'         : True,
			'showSeparator' : False,
			'minWidth'      : 220,
			'items'         : [{
				'xtype'          : 'combobox',
				'itemId'         : 'docid',
				'displayField'   : 'name',
				'valueField'     : 'docid',
				'editable'       : False,
				'forceSelection' : False,
				'store'          : { 'type' : 'documents_Document' },
				'margin'         : 2,
				'emptyText'      : loc.translate(_('Choose document template…'))
			}, {
				'xtype'      : 'docbutton',
				'text'       : loc.translate(_('Generate')),
				'iconCls'    : 'ico-print',
				'margin'     : 2,
				'objectType' : 'entity'
			}]
		}
	}
	npform = cont['items'][0]
	if 'extraButtons' not in npform:
		npform['extraButtons'] = []
	npform['extraButtons'].append(button)

@extdirect_method('Document', 'prepare_template', request_as_last_param=True, permission='DOCUMENTS_GENERATE')
def _dyn_prep_tpl(params, req):
	objid = params.get('objid')
	objtype = params.get('objtype')
	if (not objid) or (not objtype):
		raise ValueError('No object specified')
	docid = params.get('docid')
	if not docid:
		raise ValueError('No document specified')

	sess = DBSession()
	docid = int(docid)
	doc = sess.query(Document).get(docid)
	if not doc:
		raise KeyError('No such document')

	config = {
		'docid' : docid,
		'code'  : doc.code,
		'name'  : doc.name,
		'type'  : doc.type,
		'vars'  : doc.variables,
		'body'  : doc.body
	}
	tpl_vars = {}
	form_fields = []
	req.run_hook('documents.gen.object', tpl_vars, objid, objtype, req)
	req.run_hook('documents.gen.variables', tpl_vars, doc.variables, req)

	return {
		'success' : True,
		'doc'     : config,
		'vars'    : tpl_vars,
		'form'    : form_fields
	}

