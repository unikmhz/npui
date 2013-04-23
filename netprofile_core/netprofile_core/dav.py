#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import io
import re
import itertools
import logging
import datetime as dt
from zope.interface import implementer

from pyramid.view import (
	notfound_view_config,
	view_config,
	view_defaults
)
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import (
	Allow, Deny,
	Everyone, Authenticated,
	DENY_ALL,
	authenticated_userid,
	has_permission
)
from sqlalchemy.orm.exc import NoResultFound
from netprofile import dav
from netprofile.dav import dprops
from netprofile.db.connection import DBSession
from .models import (
	DAVLock,
	File,
	FileFolder,
	Group,
	User,

	F_DEFAULT_FILES,
	F_DEFAULT_DIRS,

	F_OWNER_READ,
	F_OWNER_WRITE,
	F_OWNER_EXEC,
	F_GROUP_READ,
	F_GROUP_WRITE,
	F_GROUP_EXEC,
	F_OTHER_READ,
	F_OTHER_WRITE,
	F_OTHER_EXEC,

	global_setting
)

logger = logging.getLogger(__name__)

_re_if = re.compile(
	r'(?:<(?P<uri>.*?)>\s)?\((?P<not>Not\s)?(?:<(?P<token>[^>]*)>)?(?:\s?)(?:\[(?P<etag>[^\]]*)\])?\)',
	re.I | re.M
)

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

	@property
	def __acl__(self):
		user = self.req.user
		root = user.group.effective_root_folder
		if root:
			rights = root.rights
			ff_user = 'u:%s' % root.user.login
			ff_group = 'g:%s' % root.group.name
		else:
			try:
				root_user = sess.query(User).get(global_setting('vfs_root_uid'))
				root_group = sess.query(Group).get(global_setting('vfs_root_gid'))
			except NoResultFound:
				return (DENY_ALL,)
			ff_user = 'u:%s' % root_user.login
			ff_group = 'g:%s' % root_group.name
			rights = global_setting('vfs_root_rights')
		return (
			(Allow if (rights & F_OWNER_EXEC) else Deny, ff_user, 'access'),
			(Allow if (rights & F_OWNER_READ) else Deny, ff_user, 'read'),
			(Allow if (rights & F_OWNER_WRITE) else Deny, ff_user, 'write'),
			(Allow if (rights & F_OWNER_EXEC) else Deny, ff_user, 'execute'),
			(Allow if (rights & F_OWNER_WRITE) else Deny, ff_user, 'create'),
			(Allow if (rights & F_OWNER_WRITE) else Deny, ff_user, 'delete'),

			(Allow if (rights & F_GROUP_EXEC) else Deny, ff_group, 'access'),
			(Allow if (rights & F_GROUP_READ) else Deny, ff_group, 'read'),
			(Allow if (rights & F_GROUP_WRITE) else Deny, ff_group, 'write'),
			(Allow if (rights & F_GROUP_EXEC) else Deny, ff_group, 'execute'),
			(Allow if (rights & F_GROUP_WRITE) else Deny, ff_group, 'create'),
			(Allow if (rights & F_GROUP_WRITE) else Deny, ff_group, 'delete'),

			(Allow if (rights & F_OTHER_EXEC) else Deny, Everyone, 'access'),
			(Allow if (rights & F_OTHER_READ) else Deny, Everyone, 'read'),
			(Allow if (rights & F_OTHER_WRITE) else Deny, Everyone, 'write'),
			(Allow if (rights & F_OTHER_EXEC) else Deny, Everyone, 'execute'),
			(Allow if (rights & F_OTHER_WRITE) else Deny, Everyone, 'create'),
			(Allow if (rights & F_OTHER_WRITE) else Deny, Everyone, 'delete'),

			DENY_ALL
		)

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

	def dav_append(self, req, ctx, name):
		if isinstance(ctx, File):
			ctx.folder = None
			ctx.filename = name
		elif isinstance(ctx, FileFolder):
			ctx.parent = None
			ctx.name = name

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

@implementer(dav.IDAVCollection)
class DAVPluginUsers(dav.DAVPlugin):
	def __iter__(self):
		sess = DBSession()
		for t in sess.query(User.login):
			yield t[0]

	def __getitem__(self, name):
		sess = DBSession()
		try:
			u = sess.query(User).filter(User.login == name).one()
		except NoResultFound:
			raise KeyError('No such file or directory')
		u.__req__ = self.req
		u.__parent__ = self
		return u

	@property
	def dav_children(self):
		sess = DBSession()
		for u in sess.query(User):
			u.__req__ = self.req
			u.__parent__ = self
			yield u

@implementer(dav.IDAVCollection)
class DAVPluginGroups(dav.DAVPlugin):
	def __iter__(self):
		sess = DBSession()
		for t in sess.query(Group.name):
			yield t[0]

	def __getitem__(self, name):
		sess = DBSession()
		try:
			g = sess.query(Group).filter(Group.name == name).one()
		except NoResultFound:
			raise KeyError('No such file or directory')
		g.__req__ = self.req
		g.__parent__ = self
		return g

	@property
	def dav_children(self):
		sess = DBSession()
		for g in sess.query(Group):
			g.__req__ = self.req
			g.__parent__ = self
			yield g

@notfound_view_config(request_method='OPTIONS')
@view_config(route_name='core.home', request_method='OPTIONS')
def root_options(request):
	return DAVCollectionHandler(request).notfound_options()

class DAVHandler(object):
	def __init__(self, req):
		self.req = req

	def conditional_request(self, ctx):
		req = self.req
		etag = getattr(ctx, 'etag', None)
		if etag:
			if etag not in req.if_match:
				raise dav.DAVPreconditionError(
					'If-Match was present in the request, and it didn\'t match.',
					header='If-Match'
				)
			if etag in req.if_none_match:
				raise dav.DAVPreconditionError(
					'If-None-Match was present in the request, and it matched.',
					header='If-None-Match'
				)
		mtime = getattr(ctx, 'modification_time', None)
		if mtime:
			since = req.if_unmodified_since
			if since and (mtime > since):
				raise dav.DAVPreconditionError(
					'If-Unmodified-Since was present in the request, and resource has newer modification time.',
					header='If-Unmodified-Since'
				)

		# TODO: Move this into separe method when SYNC comes around
		if ctx:
			path = req.dav.get_ctx_path(ctx)
		else:
			path = req.dav.get_path(req.path)
		oldlocks = []
		meth = req.method
		if meth == 'DELETE':
			oldlocks.extend(req.dav.get_locks(path, True))
		elif meth in {'MKCOL', 'MKCALENDAR', 'PROPPATCH', 'PUT', 'PATCH'}:
			oldlocks.extend(req.dav.get_locks(path, False))
		elif meth == 'MOVE':
			oldlocks.extend(req.dav.get_locks(path, True))
			dest = req.dav.get_path(req.headers.get('Destination'))
			if not dest:
				raise KeyError('Destination')
			oldlocks.extend(req.dav.get_locks(dest, False))
		elif meth == 'COPY':
			dest = req.dav.get_path(req.headers.get('Destination'))
			if not dest:
				raise KeyError('Destination')
			oldlocks.extend(req.dav.get_locks(dest, False))
		lockidx = {}
		for lock in oldlocks:
			lockidx[lock.token] = lock
		oldlocks = list(lockidx.values())
		del lockidx
		ifh = self.get_if()
		if not ifh:
			ifh = []
		# TODO: This part is nasty! Rewrite it.
		for ifobj in ifh:
			for token in ifobj['tokens']:
				if 'tok' not in token:
					continue
				if token['tok'][:16] != 'opaquelocktoken:':
					continue
				tok = token['tok'][16:]
				found = None
				for il, lock in enumerate(oldlocks):
					if lock.token == tok:
						token['valid'] = True
						found = il
						break
				if found is not None:
					del oldlocks[found]
					continue

				for xlock in req.dav.get_locks(ifobj['uri']):
					if xlock.token == tok:
						token['valid'] = True
						break

		raise_exc = None
		if len(oldlocks) > 0:
			raise_exc = dav.DAVLockedError(lock=oldlocks[0])

		for ifobj in ifh:
			uri = ifobj['uri']
			all_valid = False
			for token in ifobj['tokens']:
				if 'tok' in token:
					tok_valid = token.get('valid', False)
				else:
					tok_valid = True
				if token.get('etag'):
					etag_valid = False
				else:
					etag_valid = True
				if tok_valid and (not etag_valid):
					check_etag = None
					if ctx and (uri == path):
						try:
							check_etag = '"%s"' % ctx.etag
						except AttributeError:
							pass
					else:
						root = dav.DAVRoot(req)
						try:
							full_uri = req.route_url('core.dav', traverse=(root.get_uri() + uri))
							tr = root.resolve_uri(full_uri, True)
							check_etag = '"%s"' % tr.context.etag
						except (ValueError, AttributeError):
							pass
					if (check_etag is not None) and (token.get('etag') == check_etag):
						etag_valid = True
					# Following can be totally wrong
					elif not token.get('not'):
						raise_exc = dav.DAVPreconditionError(
							'Unable to validate token and/or etag for URL:%s.' % '/'.join(uri),
							header='If'
						)
				if (tok_valid and etag_valid) ^ token.get('not'):
					all_valid = True
					break

			if not all_valid:
				raise dav.DAVPreconditionError(
					'Unable to validate token and/or etag for URL:%s.' % '/'.join(uri),
					header='If'
				)
		if raise_exc:
			raise raise_exc

	def prepare_copy_move(self):
		req = self.req
		ctx = req.context

		dest_url = req.headers.get('Destination')
		if not dest_url:
			raise dav.DAVBadRequestError('Destination URL must be supplied via Destination: HTTP header.')
		root = dav.DAVRoot(req)
		try:
			tr = root.resolve_uri(dest_url)
		except ValueError:
			raise dav.DAVBadRequestError('Bad destination URL.')
		if len(tr['subpath']) > 0:
			raise dav.DAVConflictError('Unable to locate destination node.')
		over = req.headers.get('Overwrite', 'T').upper()
		if over == 'T':
			over = True
		elif over == 'F':
			over = False
		else:
			raise dav.DAVBadRequestError('You must supply either "T" or "F" as Overwrite: HTTP header.')
		if (not tr['view_name']) and (not over):
			raise dav.DAVPreconditionError(
				'Destination node exists and overwrite was disabled via HTTP Overwrite: header.',
				header='Overwrite'
			)
		if tr['view_name']:
			parent = tr['context']
			node = None
			node_name = tr['view_name']
		else:
			node = tr['context']
			parent = node.__parent__
			node_name = node.__name__
		return (parent, node, node_name)

	def get_if(self):
		req = self.req

		ifh = req.headers.get('If')
		if ifh is None:
			return None
		ret = []
		last = None
		# TODO: normalize URIs
		for m in _re_if.finditer(ifh):
			if (not m.group('uri')) and last:
				last['tokens'].append({
					'not'   : bool(m.group('not')),
					'tok'   : m.group('token'),
					'etag'  : m.group('etag'),
					'valid' : False
				})
			else:
				uri = m.group('uri')
				if uri:
					uri = req.dav.get_path(uri)
				else:
					uri = req.dav.get_path(req.url)
				if not uri:
					raise dav.DAVForbiddenError('Invalid URI supplied in If: header.')
				last = {
					'uri'    : uri,
					'tokens' : [{
						'not'   : bool(m.group('not')),
						'tok'   : m.group('token'),
						'etag'  : m.group('etag'),
						'valid' : False
					}]
				}
				ret.append(last)
		return ret

	def proppatch(self):
		req = self.req
		self.conditional_request(req.context)
		ppreq = dav.DAVPropPatchRequest(req)
		pdict = ppreq.get_props()
		props = req.dav.set_node_props(req, req.context, pdict)
		# TODO: handle 'minimal' flags
		resp = dav.DAVMultiStatusResponse()
		el = dav.DAVResponseElement(req, req.context, props)
		resp.add_element(el)
		resp.make_body()
		resp.vary = ('Brief', 'Prefer')
		return resp

	def delete(self):
		req = self.req
		self.conditional_request(req.context)
		req.dav.delete(req, req.context)
		resp = dav.DAVDeleteResponse()
		return resp

	def propfind(self):
		req = self.req
		pfreq = dav.DAVPropFindRequest(req)
		pset = pfreq.get_props()
		depth = req.dav.get_http_depth(req, 1)
		if depth != 0:
			depth = 1
		props = req.dav.get_path_props(req, req.context, pset, depth)
		# TODO: handle 'minimal' flags
		resp = dav.DAVMultiStatusResponse()
		for ctx, node_props in props.items():
			el = dav.DAVResponseElement(self.req, ctx, node_props)
			resp.add_element(el)
		resp.make_body()
		self.req.dav.set_features(resp)
		resp.vary = ('Brief', 'Prefer')
		return resp

	def move(self):
		req = self.req
		ctx = req.context
		self.conditional_request(ctx)
		parent, node, node_name = self.prepare_copy_move()
		if node == ctx:
			raise dav.DAVForbiddenError('Can\'t move a node onto itself.')
		over = False
		if node:
			over = True
			req.dav.delete(req, node)
		appender = getattr(parent, 'dav_append', None)
		if appender is None:
			raise dav.DAVNotImplementedError('Unable to move node.')
		appender(req, ctx, node_name)
		if over:
			resp = dav.DAVOverwriteResponse()
		else:
			resp = dav.DAVCreateResponse()
		return resp

	def copy(self):
		req = self.req
		ctx = req.context
		self.conditional_request(ctx)
		parent, node, node_name = self.prepare_copy_move()
		if node == ctx:
			raise dav.DAVForbiddenError('Can\'t copy a node onto itself.')
		over = False
		if node:
			over = True
			req.dav.delete(req, node)
		appender = getattr(parent, 'dav_append', None)
		if appender is None:
			raise dav.DAVNotImplementedError('Unable to copy node.')
		new_ctx = req.dav.clone(req, ctx)
		appender(req, new_ctx, node_name)
		if over:
			resp = dav.DAVOverwriteResponse()
		else:
			resp = dav.DAVCreateResponse()
		return resp

	def lock(self):
		req = self.req
		ctx = req.context

		path = req.dav.get_ctx_path(ctx)
		str_path = '/'.join(path)
		locks = req.dav.get_locks(path)
		lock = None

		if req.body:
			# New lock
			oldlock = None
			for oldlock in locks:
				if oldlock.scope == DAVLock.SCOPE_EXCLUSIVE:
					raise dav.DAVConflictingLockError(lock=oldlock)
			lreq = dav.DAVLockRequest(req)
			lock = lreq.get_lock(DAVLock)
			if oldlock and (lock.scope != DAVLock.SCOPE_SHARED):
				raise dav.DAVConflictingLockError(lock=oldlock)
			lock.uri = str_path
			lock.depth = req.dav.get_http_depth(req)
			if isinstance(ctx, File):
				lock.file = ctx
		else:
			# Refreshing old lock
			ifh = self.get_if()
			if not ifh:
				raise dav.DAVBadRequestError('No If: headers supplied in LOCK refresh request.')
			try:
				for oldlock in locks:
					for ifobj in ifh:
						for token in ifobj['tokens']:
							if oldlock.test_token(token['tok']):
								lock = oldlock
								raise StopIteration
			except StopIteration:
				pass
			if lock is None:
				if len(locks):
					raise dav.DAVLockedError('Resource is locked.', lock=locks[0])
				else:
					raise dav.DAVBadRequestError('New LOCK request must be accompanied by a request body.')

		lock.refresh(req.dav.get_http_timeout(req))

		if req.body:
			sess = DBSession()
			sess.add(lock)

		resp = dav.DAVLockResponse(lock=lock, request=req, new_file=False)
		resp.make_body()
		return resp

	def unlock(self):
		req = self.req
		ctx = req.context

		token = req.headers.get('Lock-Token')
		if not token:
			raise dav.DAVBadRequestError('UNLOCK request must be accompanied by a valid lock token header.')
		path = req.dav.get_ctx_path(ctx)
		if token[0] != '<':
			token = '<%s>' % (token,)
		locks = req.dav.get_locks(path)
		for lock in locks:
			token_str = '<opaquelocktoken:%s>' % (lock.token,)
			if token == token_str:
				sess = DBSession()
				sess.delete(lock)
				return dav.DAVUnlockResponse()
		raise dav.DAVLockTokenMatchError('Invalid lock token supplied.')

	def report(self):
		req = self.req
		rreq = dav.DAVReportRequest(req)
		rname = rreq.get_name()
		if rname is None:
			raise dav.DAVBadRequestError('Need to supply report name.')
		r = req.dav.report(rname, rreq)
		return r(req)

@view_defaults(route_name='core.dav', context=dav.IDAVCollection, decorator=dav_decorator)
class DAVCollectionHandler(DAVHandler):
	@notfound_view_config(containment=dav.IDAVCollection, decorator=dav_decorator)
	def notfound_generic(self):
		raise dav.DAVNotFoundError('Node not found.')

	@view_config(request_method='OPTIONS')
	def options(self):
		resp = Response()
		self.req.dav.set_headers(resp)
		self.req.dav.set_allow(resp)
		return resp

	@notfound_view_config(request_method='OPTIONS', containment=dav.IDAVCollection, decorator=dav_decorator)
	def notfound_options(self):
		resp = Response()
		self.req.dav.set_headers(resp)
		self.req.dav.set_allow(resp, ('MKCOL',))
		return resp

	# TODO: Make this into file browser
	@notfound_view_config(request_method='GET', containment=dav.IDAVCollection)
	def notfound_get(self):
		return HTTPNotFound()

	@view_config(request_method='MKCOL')
	def mkcol(self):
		# Try to create collection on top of existing collection
		raise dav.DAVMethodNotAllowedError(*self.req.dav.methods)

	@notfound_view_config(request_method='MKCOL', containment=dav.IDAVCollection, decorator=dav_decorator)
	def notfound_mkcol(self):
		mcreq = dav.DAVMkColRequest(self.req)
		resp = mcreq.process()
		return resp

	@view_config(request_method='PROPFIND')
	def propfind(self):
		return super(DAVCollectionHandler, self).propfind()

	@view_config(request_method='PROPPATCH')
	def proppatch(self):
		return super(DAVCollectionHandler, self).proppatch()

	@view_config(request_method='DELETE')
	def delete(self):
		return super(DAVCollectionHandler, self).delete()

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
		resp = dav.DAVCreateResponse(etag=etag)
		return resp

	@view_config(request_method='REPORT')
	def report(self):
		return super(DAVCollectionHandler, self).report()

	@view_config(request_method='MOVE')
	def move(self):
		return super(DAVCollectionHandler, self).move()

	@view_config(request_method='COPY')
	def copy(self):
		return super(DAVCollectionHandler, self).copy()

	@view_config(request_method='LOCK')
	def lock(self):
		return super(DAVCollectionHandler, self).lock()

	@notfound_view_config(request_method='LOCK', containment=dav.IDAVCollection, decorator=dav_decorator)
	def notfound_lock(self):
		# TODO: DRY, unify this with normal lock
		req = self.req

		path = req.dav.get_path(req.url)
		str_path = '/'.join(path)
		locks = req.dav.get_locks(path)
		lock = None

		if req.body:
			# New lock
			oldlock = None
			for oldlock in locks:
				if oldlock.scope == DAVLock.SCOPE_EXCLUSIVE:
					raise dav.DAVConflictingLockError(lock=oldlock)
			lreq = dav.DAVLockRequest(req)
			lock = lreq.get_lock(DAVLock)
			if oldlock and (lock.scope != DAVLock.SCOPE_SHARED):
				raise dav.DAVConflictingLockError(lock=oldlock)
			lock.uri = str_path
			lock.depth = req.dav.get_http_depth(req)
		else:
			# Refreshing old lock
			ifh = self.get_if()
			if not ifh:
				raise dav.DAVBadRequestError('No If: headers supplied in LOCK refresh request.')
			try:
				for oldlock in locks:
					for ifobj in ifh:
						for token in ifobj['tokens']:
							if oldlock.test_token(token['tok']):
								lock = oldlock
								raise StopIteration
			except StopIteration:
				pass
			if lock is None:
				if len(locks):
					raise dav.DAVLockedError('Resource is locked.', lock=locks[0])
				else:
					raise dav.DAVBadRequestError('New LOCK request must be accompanied by a request body.')

		if not req.view_name:
			# TODO: find proper DAV error to put here
			raise Exception('Invalid file name (empty file names are not allowed).')
		if len(req.subpath) > 0:
			# TODO: find proper DAV error to put here
			raise Exception('Invalid file name (slashes are not allowed).')
		creator = getattr(req.context, 'dav_create', None)
		if creator is None:
			raise dav.DAVNotImplementedError('Unable to create child node.')
		with io.BytesIO(b'') as bio:
			obj = creator(req, req.view_name, None, None, bio) # TODO: handle IOErrors, handle non-seekable request body
		if isinstance(obj, File):
			lock.file = obj
		lock.refresh(req.dav.get_http_timeout(req))

		if req.body:
			sess = DBSession()
			sess.add(lock)

		resp = dav.DAVLockResponse(lock=lock, request=req, new_file=True)
		resp.make_body()
		return resp

	@view_config(request_method='UNLOCK')
	def unlock(self):
		return super(DAVCollectionHandler, self).unlock()

@view_defaults(route_name='core.dav', context=dav.IDAVFile, decorator=dav_decorator)
class DAVFileHandler(DAVHandler):
	@view_config(request_method='GET')
	def get(self):
		return self.req.context.dav_get(self.req)

	@view_config(request_method='PROPFIND')
	def propfind(self):
		return super(DAVFileHandler, self).propfind()

	@view_config(request_method='PROPPATCH')
	def proppatch(self):
		return super(DAVFileHandler, self).proppatch()

	@view_config(request_method='DELETE')
	def delete(self):
		return super(DAVFileHandler, self).delete()

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
		raise dav.DAVMethodNotAllowedError(*self.req.dav.methods)

	@view_config(request_method='REPORT')
	def report(self):
		return super(DAVFileHandler, self).report()

	@view_config(request_method='MOVE')
	def move(self):
		return super(DAVFileHandler, self).move()

	@view_config(request_method='COPY')
	def copy(self):
		return super(DAVFileHandler, self).copy()

	@view_config(request_method='LOCK')
	def lock(self):
		return super(DAVFileHandler, self).lock()

	@view_config(request_method='UNLOCK')
	def unlock(self):
		return super(DAVFileHandler, self).unlock()

