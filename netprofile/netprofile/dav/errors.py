#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
	'DAVError',
	'DAVBadRequestError',
	'DAVNotAuthenticatedError',
	'DAVForbiddenError',
	'DAVNotFoundError',
	'DAVInvalidResourceTypeError',
	'DAVReportNotSupportedError',
	'DAVNeedPrivilegesError',
	'DAVMethodNotAllowedError',
	'DAVConflictError',
	'DAVLockTokenMatchError',
	'DAVACEConflictError',
	'DAVPreconditionError',
	'DAVNoAbstractPrivilegeError',
	'DAVNotRecognizedPrincipalError',
	'DAVNotSupportedPrivilegeError',
	'DAVUnsupportedMediaTypeError',
	'DAVLockedError',
	'DAVConflictingLockError',
	'DAVNotImplementedError'
]

from lxml import etree

from . import props as dprops
from .values import DAVValue

class DAVError(RuntimeError, DAVValue):
	def __init__(self, *args, status=500):
		super(DAVError, self).__init__(*args)
		self.status = status

	def render(self, parent):
		pass

	def response(self, resp):
		pass

class DAVBadRequestError(DAVError):
	def __init__(self, *args):
		super(DAVBadRequestError, self).__init__(*args, status=400)

class DAVNotAuthenticatedError(DAVError):
	def __init__(self, *args):
		super(DAVNotAuthenticatedError, self).__init__(*args, status=401)

class DAVForbiddenError(DAVError):
	def __init__(self, *args):
		super(DAVForbiddenError, self).__init__(*args, status=403)

class DAVNotFoundError(DAVError):
	def __init__(self, *args):
		super(DAVNotFoundError, self).__init__(*args, status=404)

class DAVInvalidResourceTypeError(DAVForbiddenError):
	def render(self, parent):
		etree.SubElement(parent, dprops.VALID_RESOURCETYPE)
		super(DAVInvalidResourceTypeError, self).render(parent)

class DAVReportNotSupportedError(DAVForbiddenError):
	def render(self, parent):
		etree.SubElement(parent, dprops.SUPPORTED_REPORT)
		super(DAVReportNotSupportedError, self).render(parent)

class DAVNeedPrivilegesError(DAVForbiddenError):
	def __init__(self, uri, privileges):
		if not isinstance(privileges, (list, set, tuple)):
			privileges = (privileges,)
		self.uri = uri
		self.priv = privileges
		msg = 'Requested privileges for URL "%s" not satisfiable: %s' % (
			uri,
			', '.join(privileges)
		)
		super(DAVNeedPrivilegesError, self).__init__(msg)

	def render(self, parent):
		need = etree.SubElement(parent, dprops.NEED_PRIVILEGES)
		for p in self.priv:
			res = etree.SubElement(need, dprops.RESOURCE)
			el = etree.SubElement(res, dprops.HREF)
			# Need absolute URIs
			el.text = self.uri
			el = etree.SubElement(res, dprops.PRIVILEGE)
			el.text = p
		super(DAVNeedPrivilegesError, self).render(parent)

class DAVMethodNotAllowedError(DAVError):
	def __init__(self, *args):
		super(DAVMethodNotAllowedError, self).__init__(*args, status=405)

class DAVConflictError(DAVError):
	def __init__(self, *args):
		super(DAVConflictError, self).__init__(*args, status=409)

class DAVLockTokenMatchError(DAVConflictError):
	def render(self, parent):
		etree.SubElement(parent, dprops.LOCK_TOKEN_REQUEST_URI)
		super(DAVLockTokenMatchError, self).render(parent)

class DAVACEConflictError(DAVConflictError):
	def render(self, parent):
		etree.SubElement(parent, dprops.NO_ACE_CONFLICT)
		super(DAVACEConflictError, self).render(parent)

class DAVPreconditionError(DAVError):
	def __init__(self, *args, header=None):
		super(DAVPreconditionError, self).__init__(*args, status=412)
		self.header = header

class DAVNoAbstractPrivilegeError(DAVPreconditionError):
	def render(self, parent):
		etree.subElement(parent, dprops.NO_ABSTRACT)
		super(DAVNoAbstractPrivilegeError, self).render(parent)

class DAVNotRecognizedPrincipalError(DAVPreconditionError):
	def render(self, parent):
		etree.subElement(parent, dprops.RECOGNIZED_PRINCIPAL)
		super(DAVNotRecognizedPrincipalError, self).render(parent)

class DAVNotSupportedPrivilegeError(DAVPreconditionError):
	def render(self, parent):
		etree.subElement(parent, dprops.NOT_SUPPORTED_PRIVILEGE)
		super(DAVNotSupportedPrivilegeError, self).render(parent)

class DAVUnsupportedMediaTypeError(DAVError):
	def __init__(self, *args):
		super(DAVUnsupportedMediaTypeError, self).__init__(*args, status=415)

class DAVLockedError(DAVError):
	def __init__(self, *args, lock=None):
		super(DAVLockedError, self).__init__(*args, status=423)
		self.lock = lock

	def render(self, parent):
		err = etree.SubElement(parent, dprops.LOCK_TOKEN_SUBMITTED)
		if self.lock:
			href = etree.SubElement(err, dprops.HREF)
			href.text = self.lock.uri

class DAVConflictingLockError(DAVLockedError):
	def render(self, parent):
		err = etree.SubElement(parent, dprops.NO_CONFLICTING_LOCK)
		if self.lock:
			href = etree.SubElement(err, dprops.HREF)
			href.text = self.lock.uri

class DAVNotImplementedError(DAVError):
	def __init__(self, *args):
		super(DAVNotImplementedError, self).__init__(*args, status=501)

	def response(self, resp):
		resp.allow = self.args

