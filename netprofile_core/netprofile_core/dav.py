#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import itertools
import logging
from zope.interface import implementer

from pyramid.view import (
	notfound_view_config,
	view_config,
	view_defaults
)
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import authenticated_userid
from sqlalchemy.orm.exc import NoResultFound
from netprofile import dav
from netprofile.dav import dprops
from netprofile.db.connection import DBSession
from .models import (
	File,
	FileFolder,
	F_DEFAULT_FILES,
	F_DEFAULT_DIRS
)

logger = logging.getLogger(__name__)

def dav_decorator(view):
	def dav_request(context, request):
		logger.debug('Running WebDAV request: path=%r, method=%r, view_name=%r, subpath=%r' % (
			request.path,
			request.method,
			request.view_name,
			request.subpath
		))
		try:
			userid = authenticated_userid(request)
			if userid is None:
				raise dav.DAVNotAuthenticatedError()
			return view(context, request)
		except dav.DAVError as e:
			resp = dav.DAVErrorResponse(error=e)
			resp.www_authenticate = request.response.www_authenticate
			resp.make_body()
			return resp
	return dav_request

@implementer(dav.IDAVCollection)
class DAVPluginVFS(dav.DAVPlugin):
	def __iter__(self):
		user = self.req.user
		root = None
		if user:
			root = user.group.effective_root_folder
		sess = DBSession()
		# TODO: add access controls
		for t in sess.query(FileFolder.name).filter(FileFolder.parent == root):
			yield t[0]
		for t in sess.query(File.filename).filter(File.folder == root):
			yield t[0]

	def __getitem__(self, name):
		user = self.req.user
		root = None
		if user:
			root = user.group.effective_root_folder
		sess = DBSession()
		# TODO: add access controls
		try:
			f = sess.query(FileFolder).filter(FileFolder.parent == root, FileFolder.name == name).one()
		except NoResultFound:
			try:
				f = sess.query(File).filter(File.folder == root, File.filename == name).one()
			except NoResultFound:
				raise KeyError('No such file or directory')
		f.__req__ = self.req
		f.__parent__ = self
		return f

	def get_uri(self):
		uri = self.__parent__.get_uri()
		uri.append(self.__name__)
		return uri

	def dav_props(self, pset):
		ret = {}
		if dprops.RESOURCE_TYPE in pset:
			ret[dprops.RESOURCE_TYPE] = dav.DAVResourceTypeValue(dprops.COLLECTION)
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = 'fs'
		return ret

	def dav_create(self, req, name, rtype=None, props=None, data=None):
		# TODO: externalize type resolution
		user = req.user
		sess = DBSession()
		if rtype and (dprops.COLLECTION in rtype):
			obj = FileFolder(
				user_id=user.id,
				group_id=user.group_id,
				name=name,
				parent=None,
				rights=F_DEFAULT_DIRS
			)
			sess.add(obj)
		else:
			obj = File(
				user_id=user.id,
				group_id=user.group_id,
				filename=name,
				name=name,
				folder=None,
				rights=F_DEFAULT_FILES
			)
			sess.add(obj)
			if data is not None:
				# TODO: detect type of data (fd / buffer)
				obj.set_from_file(data, user, sess)
			if props and (dprops.CONTENT_TYPE in props):
				obj.mime_type = props[dprops.CONTENT_TYPE]
		if props:
			if dprops.CREATION_DATE in props:
				obj.creation_time = props[dprops.CREATION_DATE]
			if dprops.LAST_MODIFIED in props:
				obj.modification_time = props[dprops.LAST_MODIFIED]
		return obj

	@property
	def dav_children(self):
		user = self.req.user
		root = None
		if user:
			root = user.group.effective_root_folder
		sess = DBSession()
		for t in itertools.chain(
			sess.query(FileFolder).filter(FileFolder.parent == root),
			sess.query(File).filter(File.folder == root)
		):
			t.__req__ = self.req
			t.__parent__ = self
			yield t

class DAVHandler(object):
	def __init__(self, req):
		self.req = req

	def set_dav_headers(self, resp):
		resp.headers.add('DAV', '1, extended-mkcol')
		resp.headers.add('MS-Author-Via', 'DAV')
		resp.accept_ranges = 'bytes'

	def conditional_request(self, ctx):
		req = self.req
		etag = getattr(ctx, 'etag', None)
		if etag:
			if etag not in req.if_match:
				raise dav.DAVPreconditionError('If-Match was present in the request, and it didn\'t match.', header='If-Match')
			if etag in req.if_none_match:
				raise dav.DAVPreconditionError('If-None-Match was present in the request, and it matched.', header='If-None-Match')
		mtime = getattr(ctx, 'modification_time', None)
		if mtime:
			since = req.if_unmodified_since
			if since and (mtime > since):
				raise dav.DAVPreconditionError('If-Unmodified-Since was present in the request, and resource has newer modification time.', header='If-Unmodified-Since')
		# TODO: handle DAV-specific If: headers

@view_defaults(route_name='core.dav', context=dav.IDAVCollection, decorator=dav_decorator)
class DAVCollectionHandler(DAVHandler):
	@notfound_view_config(containment=dav.IDAVCollection, decorator=dav_decorator)
	def notfound_generic(self):
		raise dav.DAVNotFoundError('Node not found.')

	@view_config(request_method='OPTIONS')
	def options(self):
		resp = Response()
		self.set_dav_headers(resp)
		resp.allow = ('OPTIONS', 'GET', 'HEAD', 'DELETE', 'PROPFIND', 'PUT', 'PROPPATCH', 'COPY', 'MOVE', 'REPORT', 'PATCH')
		return resp

	@notfound_view_config(request_method='OPTIONS', containment=dav.IDAVCollection, decorator=dav_decorator)
	def notfound_options(self):
		resp = Response()
		self.set_dav_headers(resp)
		resp.allow = ('OPTIONS', 'GET', 'HEAD', 'DELETE', 'PROPFIND', 'PUT', 'PROPPATCH', 'COPY', 'MOVE', 'REPORT', 'MKCOL', 'PATCH')
		return resp

	# TODO: Make this into file browser
	@notfound_view_config(request_method='GET', containment=dav.IDAVCollection)
	def notfound_get(self):
		return HTTPNotFound()

	@view_config(request_method='MKCOL')
	def mkcol(self):
		# Try to create collection on top of existing collection
		raise dav.DAVMethodNotAllowedError('OPTIONS', 'GET', 'HEAD', 'DELETE', 'PROPFIND', 'PUT', 'PROPPATCH', 'COPY', 'MOVE', 'REPORT', 'PATCH')

	@notfound_view_config(request_method='MKCOL', containment=dav.IDAVCollection, decorator=dav_decorator)
	def notfound_mkcol(self):
		mcreq = dav.DAVMkColRequest(self.req)
		resp = mcreq.process()
		return resp

	@view_config(request_method='PROPFIND')
	def propfind(self):
		pfreq = dav.DAVPropFindRequest(self.req)
		pset = pfreq.get_props()
		depth = dav.get_http_depth(self.req, 1)
		if depth != 0:
			depth = 1
		props = dav.get_path_props(self.req.context, pset, depth)
		# TODO: handle 'minimal' flags
		resp = dav.DAVMultiStatusResponse()
		for ctx, node_props in props.items():
			el = dav.DAVResponseElement(ctx, node_props)
			resp.add_element(el)
		resp.make_body()
		resp.headers.add('DAV', '1, extended-mkcol')
		resp.vary = ('Brief', 'Prefer')
		return resp

#	@notfound_view_config(request_method='PROPFIND', containment=dav.IDAVCollection, decorator=dav_decorator)
#	def notfound_propfind(self):
#		raise dav.DAVNotFoundError('Node not found.')

	@view_config(request_method='PROPPATCH')
	def proppatch(self):
		req = self.req
		self.conditional_request(req.context)
		ppreq = dav.DAVPropPatchRequest(req)
		pdict = ppreq.get_props()
		props = dav.set_node_props(req.context, pdict)
		# TODO: handle 'minimal' flags
		resp = dav.DAVMultiStatusResponse()
		el = dav.DAVResponseElement(req.context, props)
		resp.add_element(el)
		resp.make_body()
		resp.vary = ('Brief', 'Prefer')
		return resp

	@view_config(request_method='DELETE')
	def delete(self):
		req = self.req
		self.conditional_request(req.context)
		dav.dav_delete(req.context)
		resp = dav.DAVDeleteResponse()
		return resp

	@view_config(request_method='PUT')
	def put(self):
		# Try to overwrite directory with a file
		raise dav.DAVConflictError('PUT on collections is undefined.')

	@notfound_view_config(request_method='PUT', containment=dav.IDAVCollection, decorator=dav_decorator)
	def notfound_put(self):
		# Create new file
		req = self.req
		if not req.view_name:
			# TODO: find proper DAV error to put here
			raise Exception('Invalid file name (empty file names are not allowed).')
		if len(req.subpath) > 0:
			# TODO: find proper DAV error to put here
			raise Exception('Invalid file name (slashes are not allowed).')
		if req.range:
			raise dav.DAVNotImplementedError('Can\'t PUT partial content.')
		if 'If-Match' in req.headers:
			raise dav.DAVPreconditionError('If-Match was present in the request to create new file.', header='If-Match')
		creator = getattr(req.context, 'dav_create', None)
		if creator is None:
			raise dav.DAVNotImplementedError('Unable to create child node.')
		obj = creator(req, req.view_name, None, None, req.body_file_seekable) # TODO: handle IOErrors, handle non-seekable request body
		etag = getattr(obj, 'etag', None)
		resp = dav.DAVETagResponse(etag=etag)
		return resp

	@view_config(request_method='REPORT')
	def report(self):
		# TODO: write this
		raise dav.DAVReportNotSupportedError()

@view_defaults(route_name='core.dav', context=dav.IDAVFile, decorator=dav_decorator)
class DAVFileHandler(DAVHandler):
	@view_config(request_method='GET')
	def get(self):
		return self.req.context.get_response(self.req)

	@view_config(request_method='PROPFIND')
	def propfind(self):
		pfreq = dav.DAVPropFindRequest(self.req)
		pset = pfreq.get_props()
		depth = dav.get_http_depth(self.req, 1)
		if depth != 0:
			depth = 1
		props = dav.get_path_props(self.req.context, pset, depth)
		# TODO: handle 'minimal' flags
		resp = dav.DAVMultiStatusResponse()
		for ctx, node_props in props.items():
			el = dav.DAVResponseElement(ctx, node_props)
			resp.add_element(el)
		resp.make_body()
		resp.headers.add('DAV', '1, extended-mkcol')
		resp.vary = ('Brief', 'Prefer')
		return resp

	@view_config(request_method='PROPPATCH')
	def proppatch(self):
		req = self.req
		self.conditional_request(req.context)
		ppreq = dav.DAVPropPatchRequest(req)
		pdict = ppreq.get_props()
		props = dav.set_node_props(req.context, pdict)
		# TODO: handle 'minimal' flags
		resp = dav.DAVMultiStatusResponse()
		el = dav.DAVResponseElement(req.context, props)
		resp.add_element(el)
		resp.make_body()
		resp.vary = ('Brief', 'Prefer')
		return resp

	@view_config(request_method='DELETE')
	def delete(self):
		req = self.req
		self.conditional_request(req.context)
		dav.dav_delete(req.context)
		resp = dav.DAVDeleteResponse()
		return resp

	@view_config(request_method='PUT')
	def put(self):
		# Overwrite existing file
		req = self.req
		if req.range:
			raise dav.DAVNotImplementedError('Can\'t PUT partial content.')
		obj = req.context
		self.conditional_request(obj)
		putter = getattr(obj, 'dav_put', None)
		if putter is None:
			raise dav.DAVNotImplementedError('Unable to overwrite node.')
		putter(req, req.body_file_seekable) # TODO: handle IOErrors, handle non-seekable request body
		etag = getattr(obj, 'etag', None)
		resp = dav.DAVCreateResponse(etag=etag)
		return resp

	@view_config(request_method='MKCOL')
	def mkcol(self):
		# Try to create collection on top of existing file
		raise dav.DAVMethodNotAllowedError('OPTIONS', 'GET', 'HEAD', 'DELETE', 'PROPFIND', 'PUT', 'PROPPATCH', 'COPY', 'MOVE', 'REPORT', 'PATCH')

