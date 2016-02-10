#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV report objects
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
	'DAVReport',
	'DAVExpandPropertyReport',
	'DAVPrincipalPropertySearchReport',
	'DAVACLPrincipalPropertySetReport',
	'DAVPrincipalSearchPropertySetReport',
	'DAVPrincipalMatchReport',
	'DAVSyncCollectionReport',
	'DAVAddressBookQueryReport',
	'DAVAddressBookMultiGetReport'
]

from zope.interface.verify import verifyObject
from zope.interface.exceptions import DoesNotImplement

from netprofile import vobject

from . import props as dprops
from .errors import (
	DAVBadRequestError,
	DAVNotImplementedError,
	DAVInvalidSyncTokenError
)
from .values import (
	DAVBinaryValue,
	DAVHrefValue,
	DAVResponseValue
)
from .responses import (
	DAVMultiStatusResponse,
	DAVPrincipalSearchPropertySetResponse,
	DAVSyncCollectionResponse
)
from .elements import DAVResponseElement
from .interfaces import (
	IDAVAddressBook,
	IDAVCard,
	IDAVCollection
)

class DAVReport(object):
	def __init__(self, rname, rreq):
		self.name = rname
		self.rreq = rreq

	def __call__(self, req):
		raise DAVNotImplementedError('Report %s not implemented.' % self.name)

class DAVExpandPropertyReport(DAVReport):
	def __call__(self, req):
		node = self.rreq.ctx
		root = self.rreq.xml
		depth = req.dav.get_http_depth(req, 0)

		resp = self.get_props_depth(node, root, req, depth)
		resp.make_body()
		req.dav.set_features(resp, node)
		resp.vary = ('Brief', 'Prefer')
		return resp

	def parse_request(self, prop_root):
		pdict = dict()
		for prop in prop_root:
			if prop.tag != dprops.PROPERTY:
				continue
			prop_name = prop.get('name')
			if not prop_name:
				continue
			prop_ns = prop.get('namespace', dprops.NS_DAV)
			prop_id = '{%s}%s' % (prop_ns, prop_name)
			pdict[prop_id] = prop
		return pdict

	def get_props_depth(self, node, prop_root, req, depth):
		req.dav.user_acl(req, node, dprops.ACL_READ) # FIXME: parent
		pdict = self.parse_request(prop_root)

		resp = DAVMultiStatusResponse(request=req)
		props = req.dav.get_path_props(req, node, set(pdict), depth) # FIXME: get_404/minimal
		for ctx, node_props in props.items():
			if (200 in node_props) and (len(node_props[200]) > 0):
				found_props = node_props[200]
				for fprop in list(found_props):
					if fprop not in pdict:
						continue
					qprop = pdict[fprop]
					if len(qprop) == 0:
						continue
					fvalue = found_props[fprop]
					if not isinstance(fvalue, DAVHrefValue):
						continue
					fnode = fvalue.get_node(req)
					if fnode:
						found_props[fprop] = DAVResponseValue(
							fnode,
							self.get_props(fnode, qprop, req)
						)
			el = DAVResponseElement(req, ctx, node_props)
			resp.add_element(el)
		return resp

	def get_props(self, node, prop_root, req):
		req.dav.user_acl(req, node, dprops.ACL_READ) # FIXME: parent
		pdict = self.parse_request(prop_root)

		props = req.dav.get_node_props(req, node, set(pdict))
		if 200 not in props:
			return props
		found_props = props[200]
		if len(found_props) == 0:
			return props
		for fprop in list(found_props):
			if fprop not in pdict:
				continue
			qprop = pdict[fprop]
			if len(qprop) == 0:
				continue
			fvalue = found_props[fprop]
			if not isinstance(fvalue, DAVHrefValue):
				continue
			fnode = fvalue.get_node(req)
			if fnode:
				found_props[fprop] = DAVResponseValue(
					fnode,
					self.get_props(fnode, qprop, req)
				)
		return props

class DAVPrincipalPropertySearchReport(DAVReport):
	def __call__(self, req):
		req.dav.assert_http_depth(req, 0)
		root = self.rreq.xml
		nodes = (self.rreq.ctx,)

		if root.find(dprops.APPLY_TO_PRINC_COLL_SET) is not None:
			nodes = req.dav.principal_collections(req)
		test = root.get('test')
		if test not in ('allof', 'anyof'):
			test = 'allof'
		query = dict()
		pset = set()
		for cond in root.iterchildren(dprops.PROPERTY_SEARCH):
			prop = cond.find(dprops.PROP)
			match = cond.find(dprops.MATCH)
			if (prop is None) or (match is None):
				raise DAVBadRequestError('DAV:property-search term must contain one property and one match tag.')
			for pname in prop:
				query[pname.tag] = match.text
		if len(query) == 0:
			raise DAVBadRequestError('DAV:principal-property-search report request must contain at least one DAV:property-search term.')

		for prop in root.iterchildren(dprops.PROP):
			for pname in prop:
				pset.add(pname.tag)

		resp = DAVMultiStatusResponse(request=req)

		for node in nodes:
			search = getattr(node, 'dav_search_principals', None)
			if not callable(search):
				continue
			for result in search(req, test, query):
				if not req.dav.has_user_acl(req, result, dprops.ACL_READ):
					continue
				props = req.dav.get_node_props(req, result, pset)
				el = DAVResponseElement(req, result, props)
				resp.add_element(el)

		resp.make_body()
		req.dav.set_features(resp, node)
		resp.vary = ('Brief', 'Prefer')
		return resp

class DAVACLPrincipalPropertySetReport(DAVReport):
	@classmethod
	def supports(cls, node):
		acl = getattr(node, 'dav_acl', None)
		return callable(acl)

	def __call__(self, req):
		req.dav.assert_http_depth(req, 0)
		root = self.rreq.xml
		node = self.rreq.ctx
		try:
			acl = node.dav_acl(req)
		except (AttributeError, TypeError):
			raise DAVBadRequestError('Request URI does not support ACLs.')

		req.dav.user_acl(req, node, dprops.ACL_READ_ACL)
		pset = set()
		for prop in root.iterchildren(dprops.PROP):
			for pname in prop:
				pset.add(pname.tag)

		resp = DAVMultiStatusResponse(request=req)

		for princ in acl.all_principals:
			relnode = princ.related_node(req, node)
			if relnode is None:
				continue
			if req.dav.has_user_acl(req, relnode, dprops.ACL_READ):
				props = req.dav.get_node_props(req, relnode, pset)
				el = DAVResponseElement(req, relnode, props)
			else:
				el = DAVResponseElement(req, relnode, props=None, status=403)
			resp.add_element(el)

		resp.make_body()
		req.dav.set_features(resp, node)
		resp.vary = ('Brief', 'Prefer')
		return resp

class DAVPrincipalSearchPropertySetReport(DAVReport):
	@classmethod
	def supports(cls, node):
		sf = getattr(node, 'dav_search_fields', None)
		return callable(sf)

	def __call__(self, req):
		req.dav.assert_http_depth(req, 0)
		node = self.rreq.ctx
		sf = getattr(node, 'dav_search_fields', None)
		if not callable(sf):
			raise DAVBadRequestError('Request URI does not support DAV:principal-search-property-set report.')
		resp = DAVPrincipalSearchPropertySetResponse(req, sf(req))
		resp.make_body()
		return resp

class DAVPrincipalMatchReport(DAVReport):
	@classmethod
	def supports(cls, node):
		try:
			verifyObject(IDAVCollection, node)
		except DoesNotImplement:
			return False
		return True

	def __call__(self, req):
		req.dav.assert_http_depth(req, 0)
		root = self.rreq.xml
		node = self.rreq.ctx
		user = req.user
		req.dav.user_acl(req, node, dprops.ACL_READ) # FIXME: recursive

		try:
			verifyObject(IDAVCollection, node)
		except DoesNotImplement:
			raise DAVBadRequestError('DAV:principal-match report can only be run on collections.')
		find_prop = root.find(dprops.PRINC_PROP)
		if (find_prop is not None) and (len(find_prop) > 0):
			find_prop = find_prop[0].tag
		else:
			find_prop = None
		find_self = root.find(dprops.SELF)
		pset = set()
		for prop in root.iterchildren(dprops.PROP):
			for pname in prop:
				pset.add(pname.tag)

		# TODO: try to optimize this report when PRINC_PROP (find_prop) is used
		if find_prop and (find_self is not None):
			raise DAVBadRequestError('DAV:principal-match report request cannot contain both DAV:principal-property and DAV:self properties.')

		resp = DAVMultiStatusResponse(request=req)

		if find_self is not None:
			matcher = getattr(node, 'dav_match_self', None)
			if callable(matcher):
				for result in matcher(req):
					if not req.dav.has_user_acl(req, result, dprops.ACL_READ):
						continue
					if len(pset):
						props = req.dav.get_node_props(req, result, pset)
					else:
						props = None
					el = DAVResponseElement(req, result, props, 200)
					resp.add_element(el)
		elif find_prop:
			send_props = len(pset) > 0
			remove_prop = False
			if find_prop not in pset:
				pset.add(find_prop)
				remove_prop = True
			props = req.dav.get_path_props(req, node, pset, dprops.DEPTH_INFINITY)
			for ctx, node_props in props.items():
				if not req.dav.has_user_acl(req, ctx, dprops.ACL_READ):
					continue
				if 200 not in node_props:
					continue
				found_props = node_props[200]
				if find_prop not in found_props:
					continue
				fvalue = found_props[find_prop]
				if not isinstance(fvalue, DAVHrefValue):
					continue
				if fvalue.get_node(req) is user:
					if remove_prop:
						del found_props[find_prop]
					el = DAVResponseElement(
						req, ctx,
						node_props if send_props else None,
						200 if not send_props else None
					)
					resp.add_element(el)

		resp.make_body()
		req.dav.set_features(resp, node)
		resp.vary = ('Brief', 'Prefer')
		return resp

class DAVSyncCollectionReport(DAVReport):
	@classmethod
	def supports(cls, node):
		try:
			verifyObject(IDAVCollection, node)
		except DoesNotImplement:
			return False
		if not hasattr(node, 'dav_sync_token'):
			return False
		davcid = getattr(node, 'dav_collection_id', None)
		return (davcid is not None)

	def get_changes(self, req, ctx, pset, sync_token, sync_level, resp):
		changes = {}
		if sync_level != dprops.DEPTH_INFINITY:
			sync_level -= 1
		if not hasattr(ctx, 'dav_sync_token'):
			return
		for hist in req.dav.get_history(ctx, sync_token, ctx.dav_sync_token):
			changes[hist.uri] = hist
		for uri, hist in changes.items():
			if hist.is_delete:
				node = (ctx, uri, '') if hist.is_collection else (ctx, uri)
				el = DAVResponseElement(req, node, status=404)
				resp.add_element(el)
			else:
				node = ctx[uri]
				if not req.dav.has_user_acl(req, node, dprops.ACL_READ):
					continue
				props = req.dav.get_node_props(req, node, pset)
				el = DAVResponseElement(req, node, props)
				resp.add_element(el)
				if sync_level and hist.is_collection:
					self.get_changes(req, node, pset, sync_token, sync_level, resp)
		if sync_level:
			if not hasattr(ctx, 'dav_collections'):
				return
			for ch in ctx.dav_collections:
				ch_tok = getattr(ch, 'dav_sync_token', None)
				if ch_tok is None:
					continue
				if sync_token >= ch_tok:
					continue
				name = ch.__name__
				if name in changes:
					continue
				self.get_changes(req, ch, pset, sync_token, sync_level, resp)

	def __call__(self, req):
		# XXX: CardDavMate sends Depth:1 here
		#req.dav.assert_http_depth(req, 0)
		root = self.rreq.xml
		node = self.rreq.ctx
		user = req.user
		req.dav.user_acl(req, node, dprops.ACL_READ) # FIXME: recursive

		try:
			verifyObject(IDAVCollection, node)
		except DoesNotImplement:
			raise DAVBadRequestError('DAV:sync-collection report can only be run on collections.')
		sync_token = root.find(dprops.SYNC_TOKEN)
		if sync_token is not None:
			sync_token = sync_token.text
		if sync_token is not None:
			if not sync_token.startswith(dprops.NS_SYNC):
				raise DAVInvalidSyncTokenError('Invalid DAV:sync-token value specified.')
			try:
				sync_token = int(sync_token[len(dprops.NS_SYNC):])
			except (TypeError, ValueError):
				raise DAVInvalidSyncTokenError('Invalid DAV:sync-token value specified.')
		sync_level = root.find(dprops.SYNC_LEVEL)
		if sync_level is not None:
			sync_level = sync_level.text
			if sync_level == 'infinite':
				sync_level = dprops.DEPTH_INFINITY
			else:
				try:
					sync_level = int(sync_level)
				except (TypeError, ValueError):
					raise DAVBadRequestError('Invalid DAV:sync-level value specified.')
		else:
			sync_level = 1
#		sync_limit = root.find(dprops.LIMIT)
		dav_cid = node.dav_collection_id
		cur_sync_token = node.dav_sync_token
		pset = set()
		for prop in root.iterchildren(dprops.PROP):
			for pname in prop:
				pset.add(pname.tag)

		resp = DAVSyncCollectionResponse(request=req, sync_token=cur_sync_token)

		if sync_token is None:
			props = req.dav.get_path_props(req, node, pset, sync_level) # FIXME: get_404/minimal
			for ctx, node_props in props.items():
				if not req.dav.has_user_acl(req, ctx, dprops.ACL_READ):
					continue
				el = DAVResponseElement(req, ctx, node_props)
				resp.add_element(el)
		else:
			self.get_changes(req, node, pset, sync_token, sync_level, resp)

		resp.make_body()
		req.dav.set_features(resp, node)
		resp.vary = ('Brief', 'Prefer')
		return resp

class CardDAVReport(DAVReport):
	@classmethod
	def supports(cls, node):
		try:
			verifyObject(IDAVAddressBook, node)
		except DoesNotImplement:
			try:
				verifyObject(IDAVCard, node)
			except DoesNotImplement:
				return False
		return True

_vcard_propfilter_alias = {
	'mail' : 'email'
}

class DAVAddressBookQueryReport(CardDAVReport):
	def __call__(self, req):
		root = self.rreq.xml
		node = self.rreq.ctx
		depth = req.dav.get_http_depth(req, 0)
		req.dav.user_acl(req, node, dprops.ACL_READ)

		vcard_filter = root.find('./' + dprops.VCARD_FILTER)
		pset = set()
		vpset = set()
		for prop in root.iterchildren(dprops.PROP):
			for pname in prop:
				pset.add(pname.tag)
				if pname.tag == dprops.ADDRESS_DATA:
					for vprop in pname.iterchildren(dprops.VCARD_PROP):
						vpname = vprop.get('name')
						if vpname is not None:
							vpset.add(vpname)

		resp = DAVMultiStatusResponse(request=req)
		props = req.dav.get_path_props(req, node, pset, depth) # FIXME: get_404/minimal
		for ctx, node_props in props.items():
			if not req.dav.has_user_acl(req, ctx, dprops.ACL_READ):
				continue
			try:
				verifyObject(IDAVCard, ctx)
				try:
					card_data = ctx.dav_get(req).body.decode()
				except AttributeError:
					continue
				card = vobject.readOne(card_data)
				if not self.filter(req, ctx, card, vcard_filter):
					continue
				if (len(vpset) > 0) and (200 in node_props) and (dprops.ADDRESS_DATA in node_props[200]):
					newcard = vobject.vCard()
					for vpname in vpset:
						vpname_lower = vpname.lower()
						if vpname_lower not in card.contents:
							continue
						for vpval in getattr(card, vpname_lower + '_list'):
							newcard.add(vpval.duplicate(vpval))
					node_props[200][dprops.ADDRESS_DATA] = DAVBinaryValue(newcard.serialize(validate=False))
			except (DoesNotImplement, vobject.base.ParseError):
				continue
			el = DAVResponseElement(req, ctx, node_props)
			resp.add_element(el)

		resp.make_body()
		req.dav.set_features(resp, node)
		resp.vary = ('Brief', 'Prefer')
		return resp

	def filter(self, req, obj, card, filters):
		if filters is None:
			return True
		if len(filters) == 0:
			return True
		test = filters.get('test')
		if test not in ('allof', 'anyof'):
			test = 'anyof'
		for propfilter in filters.iterchildren(dprops.VCARD_PROP_FILTER):
			name = propfilter.get('name')
			if name is None:
				continue
			group = None
			if '.' in name:
				group, name = name.split('.')
			lcname = name.lower()
			if lcname in _vcard_propfilter_alias:
				lcname = _vcard_propfilter_alias[lcname]
			ftest = propfilter.get('test')
			if ftest not in ('allof', 'anyof'):
				ftest = 'anyof'
			fmatched = False if (ftest == 'anyof') else True
			flen = len(propfilter)

			exists = (lcname in card.contents)
			propvalues = []
			if exists:
				if group:
					exists = False
					for pval in getattr(card, lcname + '_list'):
						if pval.group == group:
							exists = True
							propvalues.append(pval)
				else:
					propvalues = getattr(card, lcname + '_list')
			notdef = (propfilter.find('./' + dprops.VCARD_IS_NOT_DEFINED) is not None)
			if notdef:
				flen -= 1

			if (flen == 0) or notdef:
				if notdef:
					fmatched = not exists
				else:
					fmatched = exists
			elif not exists:
				fmatched = False
			else:
				for paramfilter in propfilter.iterchildren(dprops.VCARD_PARAM_FILTER):
					res = self.filter_param(req, obj, propvalues, paramfilter)
					if (ftest == 'anyof') and res:
						fmatched = True
						break
					if (ftest == 'allof') and not res:
						fmatched = False
						break
				else:
					for textmatch in propfilter.iterchildren(dprops.VCARD_TEXT_MATCH):
						res = self.filter_text(req, obj, propvalues, textmatch)
						if (ftest == 'anyof') and res:
							fmatched = True
							break
						if (ftest == 'allof') and not res:
							fmatched = False
							break

			if (test == 'anyof') and fmatched:
				return True
			if (test == 'allof') and not fmatched:
				return False

		return False if (test == 'anyof') else True

	def filter_param(self, req, obj, propvalues, paramfilter):
		name = paramfilter.get('name')
		if name is None:
			return False
		ucname = name.upper()
		notdef = (paramfilter.find('./' + dprops.VCARD_IS_NOT_DEFINED) is not None)
		found = False
		has_terms = False
		for val in propvalues:
			if ucname not in val.params:
				continue
			found = True
			for textmatch in paramfilter.iterchildren(dprops.VCARD_TEXT_MATCH):
				has_terms = True
				if self.filter_text(req, obj, val.params[ucname], textmatch):
					return True
		if has_terms:
			return False
		return found ^ notdef

	def filter_text(self, req, obj, propvalues, textmatch):
		substr = textmatch.text
		collation = textmatch.get('collation', 'i;unicode-casemap')
		matchtype = textmatch.get('match-type', 'contains')
		negate = True if (textmatch.get('negate-condition') == 'yes') else False
		for val in propvalues:
			val = getattr(val, 'value', val)
			if req.dav.match_text(val, substr, collation, matchtype):
				break
		else:
			return negate
		return not negate

class DAVAddressBookMultiGetReport(CardDAVReport):
	def __call__(self, req):
		root = self.rreq.xml
		node = self.rreq.ctx
		req.dav.assert_http_depth(req, 0)
		req.dav.user_acl(req, node, dprops.ACL_READ)

		pset = set()
		vpset = set()
		for prop in root.iterchildren(dprops.PROP):
			for pname in prop:
				pset.add(pname.tag)
				if pname.tag == dprops.ADDRESS_DATA:
					for vprop in pname.iterchildren(dprops.VCARD_PROP):
						vpname = vprop.get('name')
						if vpname is not None:
							vpset.add(vpname)

		nodes = []
		notfound_urls = []
		for href in root.iterchildren(dprops.HREF):
			if href.text is None:
				continue
			try:
				ctx = req.dav.node(req, href.text)
			except ValueError:
				notfound_urls.append(href.text)
				continue
			nodes.append(ctx)

		if (len(nodes) == 0) and (len(notfound_urls) == 0):
			nodes = (node,)

		resp = DAVMultiStatusResponse(request=req)
		for ctx in nodes:
			if req.dav.has_user_acl(req, ctx, dprops.ACL_READ):
				props = req.dav.get_node_props(req, ctx, pset)
				if (len(vpset) > 0) and (200 in props) and (dprops.ADDRESS_DATA in props[200]):
					try:
						verifyObject(IDAVCard, ctx)
						card_data = ctx.dav_get(req).body.decode()
						card = vobject.readOne(card_data)
						newcard = vobject.vCard()
						for vpname in vpset:
							vpname_lower = vpname.lower()
							if vpname_lower not in card.contents:
								continue
							for vpval in getattr(card, vpname_lower + '_list'):
								newcard.add(vpval.duplicate(vpval))
						props[200][dprops.ADDRESS_DATA] = DAVBinaryValue(newcard.serialize(validate=False))
					except (AttributeError, DoesNotImplement, vobject.base.ParseError):
						del props[200][dprops.ADDRESS_DATA]
				el = DAVResponseElement(req, ctx, props)
			else:
				el = DAVResponseElement(req, ctx, props=None, status=403)
			resp.add_element(el)
		for uri in notfound_urls:
			el = DAVResponseElement(req, uri, props=None, status=404)
			resp.add_element(el)

		resp.make_body()
		req.dav.set_features(resp, node)
		resp.vary = ('Brief', 'Prefer')
		return resp

