#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Documents module - Models
# © Copyright 2013 Alex 'Unik' Unigovsky
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

__all__ = [
	'Document',
]

from sqlalchemy import (
	Column,
	FetchedValue,
	ForeignKey,
	Index,
	Numeric,
	PickleType,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	func,
	text
)

from sqlalchemy.orm import (
	backref,
	relationship
)

from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIString,
	DeclEnum,
	NPBoolean,
	UInt8,
	UInt32,
	UInt64,
	npbool
)
from netprofile.db.ddl import Comment
from netprofile.ext.wizards import SimpleWizard
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_documents')

class DocumentType(DeclEnum):
	"""
	Document type ENUM.
	"""
	lxdoc      = 'lxdoc',      _('lxDoc'),          10
	html_plain = 'html-plain', _('Plain HTML'),     20
	html_ext   = 'html-ext',   _('XTemplate HTML'), 30

class Document(Base):
	"""
	Document object.
	"""
	__tablename__ = 'docs_def'
	__table_args__ = (
		Comment('Documents'),
		Index('docs_def_u_code', 'code', unique=True),
		Index('docs_def_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				#'cap_menu'      : '',
				'cap_read'      : 'DOCUMENTS_LIST',
				'cap_create'    : 'DOCUMENTS_CREATE',
				'cap_edit'      : 'DOCUMENTS_EDIT',
				'cap_delete'    : 'DOCUMENTS_DELETE',
				'menu_name'     : _('Documents'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('code', 'name', 'type'),
				'form_view'     : ('code', 'name', 'type', 'external', 'body', 'descr'),
				'easy_search'   : ('code', 'name'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new document'))
			}
		}
	)
	id = Column(
		'docid',
		UInt32(),
		Sequence('docs_def_docid_seq'),
		Comment('Document ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	code = Column(
		ASCIIString(48),
		Comment('Document code'),
		nullable=False,
		info={
			'header_string' : _('Code')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Document name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	type = Column(
		DocumentType.db_type(),
		Comment('Template type'),
		nullable=False,
		default=DocumentType.html_ext,
		server_default=DocumentType.html_ext,
		info={
			'header_string' : _('Type')
		}
	)
	external = Column(
		NPBoolean(),
		Comment('Is externally stored?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('External')
		}
	)
	body = Column(
		UnicodeText(),
		Comment('Document body'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Body'),
#			'editor_xtype'  : 'htmleditor',
			'editor_xtype'  : 'tinymce_field',
			'editor_config' : {
				'tinyMCEConfig' : {
					'theme'                             : 'advanced',
					'skin'                              : 'extjs',
					'inlinepopups_skin'                 : 'extjs',
					'theme_advanced_row_height'         : 27,
					'delta_height'                      : 1,
					'schema'                            : 'html5',
					'plugins'                           : 'lists,pagebreak,style,layer,table,save,advhr,advimage,advlink,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,visualblocks,nonbreaking,xhtmlxtras,template,wordcount,advlist',

					'theme_advanced_buttons1'           : 'bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,styleselect,formatselect,fontselect,fontsizeselect',
					'theme_advanced_buttons2'           : 'cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor',
					'theme_advanced_buttons3'           : 'tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen',
					'theme_advanced_buttons4'           : 'insertlayer,moveforward,movebackward,absolute,|,styleprops,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,visualblocks,nonbreaking,template,pagebreak,restoredraft',

					'theme_advanced_toolbar_location'   : 'top',
					'theme_advanced_toolbar_align'      : 'left',
					'theme_advanced_statusbar_location' : 'bottom',

					'extended_valid_elements'           : '+tpl[if|elsif|else|for|foreach|switch|case|default]',
					'custom_elements'                   : '~tpl',
					'valid_children'                    : '+*[tpl],+tpl[*],+tbody[tpl],+body[tpl],+table[tpl],+tpl[table|tr|tpl|#text]'
				}
			}
		}
	)
	variables = Column(
		'vars',
		PickleType(),
		Comment('List of variable templates'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Variables')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	def __str__(self):
		s = self.name
		if not s:
			s = self.code
		return str(s)

