#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV errors
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
	'DAVError',
	'DAVBadRequestError',
	'DAVNotAuthenticatedError',
	'DAVForbiddenError',
	'DAVNotFoundError',
	'DAVInvalidResourceTypeError',
	'DAVReportNotSupportedError',
	'DAVNeedPrivilegesError',
	'DAVTooManyMatchesError',
	'DAVInvalidSyncTokenError',
	'DAVMethodNotAllowedError',
	'DAVConflictError',
	'DAVLockTokenMatchError',
	'DAVACEConflictError',
	'DAVLengthRequiredError',
	'DAVPreconditionError',
	'DAVNoAbstractPrivilegeError',
	'DAVNotRecognizedPrincipalError',
	'DAVNotSupportedPrivilegeError',
	'DAVUnsupportedMediaTypeError',
	'DAVUnsatisfiableRangeError',
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

	def render(self, req, parent):
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
	def render(self, req, parent):
		etree.SubElement(parent, dprops.VALID_RESOURCETYPE)
		super(DAVInvalidResourceTypeError, self).render(req, parent)

class DAVReportNotSupportedError(DAVForbiddenError):
	def render(self, req, parent):
		etree.SubElement(parent, dprops.SUPPORTED_REPORT)
		super(DAVReportNotSupportedError, self).render(req, parent)

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

	def render(self, req, parent):
		need = etree.SubElement(parent, dprops.NEED_PRIVILEGES)
		for p in self.priv:
			res = etree.SubElement(need, dprops.RESOURCE)
			el = etree.SubElement(res, dprops.HREF)
			if isinstance(self.uri, str):
				# Need absolute URIs
				el.text = req.dav.uri(req) + self.uri
			else:
				el.text = req.dav.node_uri(req, self.uri)
			el = etree.SubElement(res, dprops.PRIVILEGE)
			etree.SubElement(el, p)
		super(DAVNeedPrivilegesError, self).render(req, parent)

class DAVTooManyMatchesError(DAVForbiddenError):
	def render(self, req, parent):
		etree.SubElement(parent, dprops.MATCHES_WITHIN_LIMITS)
		super(DAVTooManyMatchesError, self).render(req, parent)

class DAVInvalidSyncTokenError(DAVForbiddenError):
	def render(self, req, parent):
		etree.SubElement(parent, dprops.VALID_SYNC_TOKEN)
		super(DAVInvalidSyncTokenError, self).render(req, parent)

class DAVMethodNotAllowedError(DAVError):
	def __init__(self, *args):
		super(DAVMethodNotAllowedError, self).__init__(*args, status=405)

class DAVConflictError(DAVError):
	def __init__(self, *args):
		super(DAVConflictError, self).__init__(*args, status=409)

class DAVLockTokenMatchError(DAVConflictError):
	def render(self, req, parent):
		etree.SubElement(parent, dprops.LOCK_TOKEN_REQUEST_URI)
		super(DAVLockTokenMatchError, self).render(req, parent)

class DAVACEConflictError(DAVConflictError):
	def render(self, req, parent):
		etree.SubElement(parent, dprops.NO_ACE_CONFLICT)
		super(DAVACEConflictError, self).render(req, parent)

class DAVLengthRequiredError(DAVError):
	def __init__(self, *args):
		super(DAVLengthRequiredError, self).__init__(*args, status=411)

class DAVPreconditionError(DAVError):
	def __init__(self, *args, header=None):
		super(DAVPreconditionError, self).__init__(*args, status=412)
		self.header = header

class DAVNoAbstractPrivilegeError(DAVPreconditionError):
	def render(self, req, parent):
		etree.subElement(parent, dprops.NO_ABSTRACT)
		super(DAVNoAbstractPrivilegeError, self).render(req, parent)

class DAVNotRecognizedPrincipalError(DAVPreconditionError):
	def render(self, req, parent):
		etree.subElement(parent, dprops.RECOGNIZED_PRINCIPAL)
		super(DAVNotRecognizedPrincipalError, self).render(req, parent)

class DAVNotSupportedPrivilegeError(DAVPreconditionError):
	def render(self, req, parent):
		etree.subElement(parent, dprops.NOT_SUPPORTED_PRIVILEGE)
		super(DAVNotSupportedPrivilegeError, self).render(req, parent)

class DAVUnsupportedMediaTypeError(DAVError):
	def __init__(self, *args):
		super(DAVUnsupportedMediaTypeError, self).__init__(*args, status=415)

class DAVUnsatisfiableRangeError(DAVError):
	def __init__(self, *args):
		super(DAVUnsatisfiableRangeError, self).__init__(*args, status=416)

class DAVLockedError(DAVError):
	def __init__(self, *args, lock=None):
		super(DAVLockedError, self).__init__(*args, status=423)
		self.lock = lock

	def render(self, req, parent):
		err = etree.SubElement(parent, dprops.LOCK_TOKEN_SUBMITTED)
		if self.lock:
			href = etree.SubElement(err, dprops.HREF)
			href.text = self.lock.uri
		super(DAVLockedError, self).render(req, parent)

class DAVConflictingLockError(DAVLockedError):
	def render(self, req, parent):
		err = etree.SubElement(parent, dprops.NO_CONFLICTING_LOCK)
		if self.lock:
			href = etree.SubElement(err, dprops.HREF)
			href.text = self.lock.uri
		super(DAVConflictingLockError, self).render(req, parent)

class DAVNotImplementedError(DAVError):
	def __init__(self, *args):
		super(DAVNotImplementedError, self).__init__(*args, status=501)

	def response(self, resp):
		resp.allow = self.args

