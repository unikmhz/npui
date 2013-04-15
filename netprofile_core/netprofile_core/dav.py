#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from zope.interface import implementer

from netprofile.dav import (
	IDAVFile,
	IDAVCollection,
	DAVRoot,
	DAVPlugin,

	DAVError,
	DAVNotFoundError,
	DAVNotAuthenticatedError,

	DAVResourceTypeValue,

	DAVPropFindRequest,
	DAVMultiStatusResponse,
	DAVErrorResponse,
	DAVResponseElement,

	get_http_depth,
	get_path_props,

	dprops
)
from pyramid.view import (
	notfound_view_config,
	view_config,
	view_defaults
)
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import authenticated_userid
from sqlalchemy.orm.exc import NoResultFound
from netprofile.db.connection import DBSession
from .models import (
	File,
	FileFolder
)

def dav_decorator(view):
	def dav_request(context, request):
		try:
			userid = authenticated_userid(request)
			if userid is None:
				raise DAVNotAuthenticatedError()
			return view(context, request)
		except DAVError as e:
			resp = DAVErrorResponse(error=e)
			resp.www_authenticate = request.response.www_authenticate
			resp.make_body()
			return resp
	return dav_request

@implementer(IDAVCollection)
class DAVPluginVFS(DAVPlugin):
	def __iter__(self):
		user = self.req.user
		root = None
		if user:
			root = user.group.effective_root_folder
#		else:
#			return iter(())
		sess = DBSession()
		# XXX: maybe add read access to root?
		q = [t[0] for t in sess.query(FileFolder.name).filter(FileFolder.parent == root)]
		q.extend(t[0] for t in sess.query(File.filename).filter(File.folder == root))
		return iter(q)

	def __getitem__(self, name):
		print('GETTIN %s' % name)
		user = self.req.user
		root = None
		if user:
			root = user.group.effective_root_folder
#		else:
#			raise KeyError('No logged-in user')
		sess = DBSession()
		# XXX: maybe add read access to root?
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
			ret[dprops.RESOURCE_TYPE] = DAVResourceTypeValue(dprops.COLLECTION)
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = 'fs'
		return ret

@view_defaults(route_name='core.dav', context=IDAVCollection, decorator=dav_decorator)
class DAVCollectionHandler(object):
	def __init__(self, req):
		self.req = req

	@view_config(request_method='OPTIONS')
	def options(self):
		f = self.req.context
		resp = Response()
		resp.headers.add('DAV', '1')
		resp.headers.add('MS-Author-Via', 'DAV')
		resp.accept_ranges = 'bytes'
		resp.allow = ('OPTIONS', 'GET', 'HEAD', 'DELETE', 'PROPFIND', 'PUT', 'PROPPATCH', 'COPY', 'MOVE', 'REPORT', 'PATCH')
		return resp

	@notfound_view_config(request_method='OPTIONS', containment=IDAVCollection)
	def notfound_options(self):
		resp = Response()
		resp.headers.add('DAV', '1')
		resp.headers.add('MS-Author-Via', 'DAV')
		resp.accept_ranges = 'bytes'
		resp.allow = ('OPTIONS', 'GET', 'HEAD', 'DELETE', 'PROPFIND', 'PUT', 'PROPPATCH', 'COPY', 'MOVE', 'REPORT', 'MKCOL', 'PATCH')
		return resp

	@view_config(request_method='GET')
	def get(self):
		f = self.req.context
		resp = Response(f.name)
		return resp

	# TODO: Make this into file browser
	@notfound_view_config(request_method='GET', containment=IDAVCollection)
	def notfound_get(self):
		return HTTPNotFound()

	@notfound_view_config(request_method='PROPFIND', containment=IDAVCollection)
	def notfound_propfind(self):
		raise DAVNotFoundError('Node not found')

	@notfound_view_config(request_method='MKCOL', containment=IDAVCollection)
	def notfound_mkcol(self):
		pass

	@view_config(request_method='PROPFIND')
	def propfind(self):
		pfreq = DAVPropFindRequest(self.req)
		pset = pfreq.get_props()
		depth = get_http_depth(self.req, 1)
		if depth != 0:
			depth = 1
		props = get_path_props(self.req.context, pset, depth)
		# TODO: handle 'minimal' flags
		resp = DAVMultiStatusResponse()
		for ctx, node_props in props.items():
			el = DAVResponseElement(ctx, node_props)
			resp.add_element(el)
		resp.make_body()
		resp.headers.add('DAV', '1')
		resp.vary = ('Brief', 'Prefer')
		return resp

@view_defaults(route_name='core.dav', context=IDAVFile, decorator=dav_decorator)
class DAVFileHandler(object):
	def __init__(self, req):
		self.req = req

	@view_config(request_method='GET')
	def get(self):
		return self.req.context.get_response(self.req)

	@view_config(request_method='PROPFIND')
	def propfind(self):
		pfreq = DAVPropFindRequest(self.req)
		pset = pfreq.get_props()
		depth = get_http_depth(self.req, 1)
		if depth != 0:
			depth = 1
		props = get_path_props(self.req.context, pset, depth)
		# TODO: handle 'minimal' flags
		#resp = DAVMultiStatusResponse(nsmap=pfreq.xml.nsmap)
		resp = DAVMultiStatusResponse()
		for ctx, node_props in props.items():
			el = DAVResponseElement(ctx, node_props)
			resp.add_element(el)
		resp.make_body()
		resp.headers.add('DAV', '1')
		resp.vary = ('Brief', 'Prefer')
		return resp

