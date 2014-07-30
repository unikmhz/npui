#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Documents module - Models
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
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
	'DocumentBundle',
	'DocumentBundleMapping'
]

from sqlalchemy import (
	Column,
	ForeignKey,
	Index,
	PickleType,
	Sequence,
	Unicode,
	UnicodeText,
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

	bundlemap = relationship(
		'DocumentBundleMapping',
		backref=backref('document', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	bundles = association_proxy(
		'bundlemap',
		'bundle',
		creator=lambda v: DocumentBundleMapping(bundle=v)
	)

	def __str__(self):
		s = self.name
		if not s:
			s = self.code
		return str(s)

class DocumentBundle(Base):
	"""
	Group of related documents.
	"""
	__tablename__ = 'docs_bundles_def'
	__table_args__ = (
		Comment('Document bundles'),
		Index('docs_bundles_def_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				#'cap_menu'      : '',
				'cap_read'      : 'DOCUMENTS_LIST',
				'cap_create'    : 'DOCUMENTS_BUNDLES_CREATE',
				'cap_edit'      : 'DOCUMENTS_BUNDLES_EDIT',
				'cap_delete'    : 'DOCUMENTS_BUNDLES_DELETE',
				'menu_name'     : _('Bundles'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 20,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('name',),
				'form_view'     : ('name',),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new bundle'))
			}
		}
	)
	id = Column(
		'dbid',
		UInt32(),
		Sequence('docs_bundles_def_dbid_seq'),
		Comment('Document bundle ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Document bundle name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)

	docmap = relationship(
		'DocumentBundleMapping',
		backref=backref('bundle', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	documents = association_proxy(
		'docmap',
		'document',
		creator=lambda v: DocumentBundleMapping(document=v)
	)

	def __str__(self):
		return str(self.name)

class DocumentBundleMapping(Base):
	"""
	Mapping of a document to bundle.
	"""
	__tablename__ = 'docs_bundles_bits'
	__table_args__ = (
		Comment('Document bundle contents'),
		Index('docs_bundles_bits_u_doc', 'dbid', 'docid', unique=True),
		Index('docs_bundles_bits_i_docid', 'docid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				#'cap_menu'      : '',
				'cap_read'      : 'DOCUMENTS_LIST',
				'cap_create'    : 'DOCUMENTS_BUNDLES_EDIT',
				'cap_edit'      : 'DOCUMENTS_BUNDLES_EDIT',
				'cap_delete'    : 'DOCUMENTS_BUNDLES_EDIT',
				'menu_name'     : _('Bundle Contents'),
				'default_sort'  : ({ 'property': 'order', 'direction': 'ASC' },),
				'grid_view'     : ('bundle', 'document', 'order', 'copies'),
				'form_view'     : ('bundle', 'document', 'order', 'copies'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new document to the bundle'))
			}
		}
	)
	id = Column(
		'dbbid',
		UInt32(),
		Sequence('docs_bundles_bits_dbbid_seq'),
		Comment('Document bundle bit ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	bundle_id = Column(
		'dbid',
		UInt32(),
		Comment('Document bundle ID'),
		ForeignKey('docs_bundles_def.dbid', name='docs_bundles_bits_fk_dbid', onupdate='CASCADE', ondelete='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Bundle'),
			'filter_type'   : 'list',
			'column_flex'   : 1
		}
	)
	document_id = Column(
		'docid',
		UInt32(),
		Comment('Document ID'),
		ForeignKey('docs_def.docid', name='docs_bundles_bits_fk_docid', onupdate='CASCADE', ondelete='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Document'),
			'filter_type'   : 'list',
			'column_flex'   : 1
		}
	)
	order = Column(
		UInt8(),
		Comment('Order in bundle'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('Order')
		}
	)
	copies = Column(
		UInt8(),
		Comment('Number of copies'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('Copies')
		}
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.bundle),
			str(self.document)
		)

