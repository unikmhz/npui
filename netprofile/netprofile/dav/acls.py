#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV ACL objects
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

__all__ = [
	'DAVPrivilegeSetValue',
	'DAVPrivilegeValue',
	'DAVPrincipalValue',
	'DAVACEValue',
	'DAVACLValue',
	'DAVPrivilegeList',
	'DAVACLRestrictions',

	'_parse_principal',
	'_parse_ace',
	'_parse_acl'
]

from lxml import etree

from . import props as dprops
from .values import (
	DAVValue,
	DAVHrefValue
)
from .errors import DAVBadRequestError

class DAVPrivilegeSetValue(DAVValue):
	def __init__(self, privs):
		self.privs = privs

	def render(self, req, parent):
		for priv in self.privs:
			priv.render(req, parent)

class DAVPrivilegeValue(DAVValue):
	def __init__(self, name, **kwargs):
		self.name = name
		self.abstract = bool(kwargs.get('abstract', False))
		self.description = kwargs.get('description')
		self.aggregates = kwargs.get('aggregates', ())

	def render(self, req, parent):
		spriv = etree.SubElement(parent, dprops.SUPPORTED_PRIVILEGE)

		priv = etree.SubElement(spriv, dprops.PRIVILEGE)
		etree.SubElement(priv, self.name)

		if self.abstract:
			etree.SubElement(spriv, dprops.ABSTRACT)
		if self.description:
			descr = etree.SubElement(spriv, dprops.DESCRIPTION)
			descr.text = self.description

		for agg in self.aggregates:
			agg.render(req, spriv)

class DAVPrivilegeList(DAVValue):
	def __init__(self, privs):
		self.privs = privs

	def render(self, req, parent):
		for pr in self.privs:
			el = etree.SubElement(parent, dprops.PRIVILEGE)
			etree.SubElement(el, pr)

class DAVPrincipalValue(DAVValue):
	UNAUTHENTICATED = 0x01
	AUTHENTICATED   = 0x02
	HREF            = 0x03
	ALL             = 0x04
	SELF            = 0x05
	PROPERTY        = 0x06

	def __init__(self, ptype, href=None, prop=None):
		if (ptype == self.HREF) and (href is None):
			raise ValueError('HREF must be present for this principal type.')
		if (ptype == self.PROPERTY) and (prop is None):
			raise ValueError('Property name must be present for this principal type.')
		self.type = ptype
		self.href = href
		self.prop = prop

	def render(self, req, parent, prefix=False):
		if self.type == self.UNAUTHENTICATED:
			etree.SubElement(parent, dprops.UNAUTHENTICATED)
		elif self.type == self.AUTHENTICATED:
			etree.SubElement(parent, dprops.AUTHENTICATED)
		elif self.type == self.HREF:
			href = etree.SubElement(parent, dprops.HREF)
			if prefix:
				href.text = req.dav.uri(req) + self.href + '/'
			else:
				href.text = self.href + '/'
		elif self.type == self.ALL:
			etree.SubElement(parent, dprops.ACL_ALL)
		elif self.type == self.SELF:
			etree.SubElement(parent, dprops.SELF)
		elif self.type == self.PROPERTY:
			el = etree.SubElement(parent, dprops.PROPERTY)
			etree.SubElement(el, self.prop)

	def match(self, req, princ, node=None):
		if self.type == self.ALL:
			return True
		if self.type == self.AUTHENTICATED:
			return princ == req.user
		if self.type == self.UNAUTHENTICATED:
			return princ != req.user
		if self.type == self.HREF:
			try:
				target = req.dav.node(req, self.href)
			except ValueError:
				return False
			return princ.is_member_of(target)
		if self.type == self.PROPERTY:
			if node is None:
				return False
			pset = set((self.prop,))
			props = req.dav.props(req, node, pset)
			if self.prop not in props:
				return False
			val = props[self.prop]
			if not isinstance(val, DAVHrefValue):
				return False
			try:
				target = req.dav.node(req, val.value)
			except ValueError:
				return False
			return princ.is_member_of(target)
		if self.type == self.SELF:
			return princ == node
		return False

	def related_node(self, req, node=None):
		if self.type == self.HREF:
			try:
				return req.dav.node(req, self.href)
			except ValueError:
				return None
		if self.type == self.PROPERTY:
			if node is None:
				return None
			pset = set((self.prop,))
			props = req.dav.props(req, node, pset)
			if self.prop not in props:
				return None
			val = props[self.prop]
			if not isinstance(val, DAVHrefValue):
				return None
			try:
				return req.dav.node(req, val.value)
			except ValueError:
				return None
		if self.type == self.SELF:
			return node

def _parse_principal(el):
	try:
		el = el[0]
		tag = el.tag
	except IndexError:
		raise DAVBadRequestError('Invalid principal supplied.')
	if tag == dprops.UNAUTHENTICATED:
		return DAVPrincipalValue(DAVPrincipalValue.UNAUTHENTICATED)
	if tag == dprops.AUTHENTICATED:
		return DAVPrincipalValue(DAVPrincipalValue.AUTHENTICATED)
	if tag == dprops.HREF:
		return DAVPrincipalValue(DAVPrincipalValue.HREF, el.text)
	if tag == dprops.ACL_ALL:
		return DAVPrincipalValue(DAVPrincipalValue.ALL)
	if tag == dprops.SELF:
		return DAVPrincipalValue(DAVPrincipalValue.SELF)
	if tag == dprops.PROPERTY:
		try:
			prop = el[0].tag
			return DAVPrincipalValue(DAVPrincipalValue.PROPERTY, prop=prop)
		except IndexError:
			pass
	raise DAVBadRequestError('Invalid principal type supplied.')

class DAVACEValue(DAVValue):
	def __init__(self, principal, grant=(), deny=(), invert=False, protected=False):
		self.princ = principal
		self.invert = invert
		self.prot = protected
		self.grant = grant
		self.deny = deny

	def match(self, req, princ, node=None):
		if not self.princ:
			return None
		return self.princ.match(req, princ, node) ^ self.invert

	def render(self, req, parent, prefix=False):
		ace = etree.SubElement(parent, dprops.ACE)
		if self.princ:
			if self.invert:
				inv = etree.SubElement(ace, dprops.INVERT)
				el = etree.SubElement(inv, dprops.PRINCIPAL)
			else:
				el = etree.SubElement(ace, dprops.PRINCIPAL)
			self.princ.render(req, el, prefix=prefix)
		if len(self.grant) > 0:
			grant = etree.SubElement(ace, dprops.GRANT)
			for pr in self.grant:
				el = etree.SubElement(grant, dprops.PRIVILEGE)
				etree.SubElement(el, pr)
		if len(self.deny) > 0:
			deny = etree.SubElement(ace, dprops.DENY)
			for pr in self.deny:
				el = etree.SubElement(deny, dprops.PRIVILEGE)
				etree.SubElement(el, pr)
		if self.prot:
			etree.SubElement(ace, dprops.PROTECTED)

	def check(self, priv):
		if priv in self.deny:
			return False
		if priv in self.grant:
			return True
		return None

	def all_privs(self, privs):
		privs.update(self.grant)
		privs.difference_update(self.deny)

def _parse_ace(el):
	invert = False
	principal = None
	inv = el.find(dprops.INVERT)
	if inv:
		invert = True
		princs = inv.findall(dprops.PRINCIPAL)
	else:
		princs = el.findall(dprops.PRINCIPAL)
	if len(princs) != 1:
		raise DAVBadRequestError('Invalid ACE in request.')
	principal = _parse_principal(princs[0])
	protected = False
	if el.find(dprops.PROTECTED):
		protected = True
	grant = []
	deny = []
	xel = el.find(dprops.GRANT)
	if xel:
		for pr in xel:
			if pr.tag != dprops.PRIVILEGE:
				continue
			try:
				grant.append(pr[0].tag)
			except IndexError:
				pass
	xel = el.find(dprops.GRANT)
	if xel:
		for pr in xel:
			if pr.tag != dprops.PRIVILEGE:
				continue
			try:
				deny.append(pr[0].tag)
			except IndexError:
				pass
	if len(grant) and len(deny):
		raise DAVBadRequestError('Invalid ACE in request: can\'t contain both grant and deny lists.')
	return DAVACEValue(
		principal,
		grant=grant,
		deny=deny,
		invert=invert,
		protected=protected
	)

class DAVACLValue(DAVValue):
	def __init__(self, aces, prefix=False):
		self.aces = aces
		self.prefix = prefix

	def render(self, req, parent):
		for ace in self.aces:
			ace.render(req, parent, self.prefix)

	def check(self, req, princ, acl, node=None):
		if isinstance(acl, (list, tuple, set)):
			for val in acl:
				if self.check(req, princ, val, node) is not True:
					return False
			return True
		for ace in self.aces:
			if not ace.match(req, princ, node):
				continue
			ch = ace.check(acl)
			if ch is not None:
				return ch

	def all_privs(self, req, princ, node=None):
		privs = set()
		for ace in self.aces:
			if not ace.match(req, princ, node):
				continue
			ace.all_privs(privs)
		return privs

	@property
	def all_principals(self):
		for ace in self.aces:
			if ace.princ:
				yield ace.princ

def _parse_acl(el):
	aces = []
	for ace in el.iterfind(dprops.ACE):
		aces.append(_parse_ace(ace))
	return DAVACLValue(aces)

class DAVACLRestrictions(DAVValue):
	GRANT_ONLY        = 0x01
	NO_INVERT         = 0x02
	DENY_BEFORE_GRANT = 0x04

	def __init__(self, flags, required=None):
		self.flags = flags
		self.required = required

	def render(self, req, parent):
		if self.flags & self.GRANT_ONLY:
			etree.SubElement(parent, dprops.GRANT_ONLY)
		if self.flags & self.NO_INVERT:
			etree.SubElement(parent, dprops.NO_INVERT)
		if self.flags & self.DENY_BEFORE_GRANT:
			etree.SubElement(parent, dprops.DENY_BEFORE_GRANT)
		if self.required:
			for rp in self.required:
				el = etree.SubElement(parent, dprops.REQUIRED_PRINCIPAL)
				rp.render(req, el)

