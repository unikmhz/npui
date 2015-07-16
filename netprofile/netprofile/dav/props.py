#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV property lists
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

from lxml import etree

STANDARD_PROPS = set()

NS_XML        = 'http://www.w3.org/XML/1998/namespace'
NS_DAV        = 'DAV:'
NS_NETPROFILE = 'http://netprofile.ru/ns/dav/'
NS_APACHE     = 'http://apache.org/dav/props/'
NS_CALDAV     = 'urn:ietf:params:xml:ns:caldav'
NS_CARDDAV    = 'urn:ietf:params:xml:ns:carddav'
NS_MSXMLDATA  = 'urn:uuid:c2f41010-65b3-11d1-a29f-00aa00c14882/'
NS_CS         = 'http://calendarserver.org/ns/'
NS_DAVMOUNT   = 'http://purl.org/NET/webdav/mount'

NS_MAP = {
	'd'  : NS_DAV,
	'dm' : NS_DAVMOUNT,
	'cd' : NS_CALDAV,
	'ap' : NS_APACHE,
#	'dt' : NS_MSXMLDATA,
	'np' : NS_NETPROFILE
}

def _TAG(ns, name):
	return '{%s}%s' % (ns, name)

def _ACL(ns, name):
	return '{%s}%s' % (ns, name)

def _ATTR(ns, name):
	return '{%s}%s' % (ns, name)

def _PROP(ns, name):
	pn = '{%s}%s' % (ns, name)
	STANDARD_PROPS.add(pn)
	return pn

# Various constants
DEPTH_INFINITY = -1

# Property tags
ACL                     = _PROP(NS_DAV, 'acl')
ACL_RESTRICTIONS        = _PROP(NS_DAV, 'acl-restrictions')
ALTERNATE_URI_SET       = _PROP(NS_DAV, 'alternate-URI-set')
CONTENT_LENGTH          = _PROP(NS_DAV, 'getcontentlength')
CONTENT_TYPE            = _PROP(NS_DAV, 'getcontenttype')
CREATION_DATE           = _PROP(NS_DAV, 'creationdate')
CUR_USER_PRINCIPAL      = _PROP(NS_DAV, 'current-user-principal')
CUR_USER_PRIVILEGE_SET  = _PROP(NS_DAV, 'current-user-privilege-set')
DISPLAY_NAME            = _PROP(NS_DAV, 'displayname')
ETAG                    = _PROP(NS_DAV, 'getetag')
EXECUTABLE              = _PROP(NS_APACHE, 'executable')
GROUP                   = _PROP(NS_DAV, 'group')
GROUP_MEMBER_SET        = _PROP(NS_DAV, 'group-member-set')
GROUP_MEMBERSHIP        = _PROP(NS_DAV, 'group-membership')
INHERITED_ACL_SET       = _PROP(NS_DAV, 'inherited-acl-set')
IS_COLLECTION           = _PROP(NS_DAV, 'iscollection')
IS_FOLDER               = _PROP(NS_DAV, 'isFolder')
IS_HIDDEN               = _PROP(NS_DAV, 'ishidden')
LAST_MODIFIED           = _PROP(NS_DAV, 'getlastmodified')
LOCK_DISCOVERY          = _PROP(NS_DAV, 'lockdiscovery')
OWNER                   = _PROP(NS_DAV, 'owner')
PRINCIPAL_URL           = _PROP(NS_DAV, 'principal-URL')
PRINCIPAL_COLL_SET      = _PROP(NS_DAV, 'principal-collection-set')
QUOTA_AVAIL_BYTES       = _PROP(NS_DAV, 'quota-available-bytes')
QUOTA_USED_BYTES        = _PROP(NS_DAV, 'quota-used-bytes')
RESOURCE_TYPE           = _PROP(NS_DAV, 'resourcetype')
SUPPORTED_LIVE_PROP_SET = _PROP(NS_DAV, 'supported-live-property-set')
SUPPORTED_LOCK          = _PROP(NS_DAV, 'supportedlock')
SUPPORTED_PRIVILEGE_SET = _PROP(NS_DAV, 'supported-privilege-set')
SUPPORTED_REPORT_SET    = _PROP(NS_DAV, 'supported-report-set')

# Resource type tags
COLLECTION              = _TAG(NS_DAV, 'collection')
PRINCIPAL               = _TAG(NS_DAV, 'principal')

# Generic tags
ABSTRACT                = _TAG(NS_DAV, 'abstract')
ACE                     = _TAG(NS_DAV, 'ace')
ACTIVE_LOCK             = _TAG(NS_DAV, 'activelock')
ALL_PROPS               = _TAG(NS_DAV, 'allprop')
AUTHENTICATED           = _TAG(NS_DAV, 'authenticated')
DENY                    = _TAG(NS_DAV, 'deny')
DENY_BEFORE_GRANT       = _TAG(NS_DAV, 'deny-before-grant')
DEPTH                   = _TAG(NS_DAV, 'depth')
DESCRIPTION             = _TAG(NS_DAV, 'description')
ERROR                   = _TAG(NS_DAV, 'error')
EXCLUSIVE               = _TAG(NS_DAV, 'exclusive')
EXPAND_PROPERTY         = _TAG(NS_DAV, 'expand-property')
GRANT                   = _TAG(NS_DAV, 'grant')
GRANT_ONLY              = _TAG(NS_DAV, 'grant-only')
HREF                    = _TAG(NS_DAV, 'href')
INCLUDE                 = _TAG(NS_DAV, 'include')
INHERITED               = _TAG(NS_DAV, 'inherited')
INVERT                  = _TAG(NS_DAV, 'invert')
LOCK_ENTRY              = _TAG(NS_DAV, 'lockentry')
LOCK_ROOT               = _TAG(NS_DAV, 'lockroot')
LOCK_SCOPE              = _TAG(NS_DAV, 'lockscope')
LOCK_TOKEN              = _TAG(NS_DAV, 'locktoken')
LOCK_TYPE               = _TAG(NS_DAV, 'locktype')
MKCOL                   = _TAG(NS_DAV, 'mkcol')
MULTI_STATUS            = _TAG(NS_DAV, 'multistatus')
NO_INVERT               = _TAG(NS_DAV, 'no-invert')
PRINC_PROP_SEARCH       = _TAG(NS_DAV, 'principal-property-search')
PRINC_SEARCH_PROP_SET   = _TAG(NS_DAV, 'principal-search-property-set')
PRIVILEGE               = _TAG(NS_DAV, 'privilege')
PROP                    = _TAG(NS_DAV, 'prop')
PROPERTY                = _TAG(NS_DAV, 'property')
PROPERTY_UPDATE         = _TAG(NS_DAV, 'propertyupdate')
PROPFIND                = _TAG(NS_DAV, 'propfind')
PROPNAME                = _TAG(NS_DAV, 'propname')
PROPSTAT                = _TAG(NS_DAV, 'propstat')
PROTECTED               = _TAG(NS_DAV, 'protected')
REMOVE                  = _TAG(NS_DAV, 'remove')
REPORT                  = _TAG(NS_DAV, 'report')
REQUIRED_PRINCIPAL      = _TAG(NS_DAV, 'required-principal')
RESOURCE                = _TAG(NS_DAV, 'resource')
RESPONSE                = _TAG(NS_DAV, 'response')
RESPONSE_DESCRIPTION    = _TAG(NS_DAV, 'responsedescription')
SELF                    = _TAG(NS_DAV, 'self')
SET                     = _TAG(NS_DAV, 'set')
SHARED                  = _TAG(NS_DAV, 'shared')
STATUS                  = _TAG(NS_DAV, 'status')
SUPPORTED_PRIVILEGE     = _TAG(NS_DAV, 'supported-privilege')
SUPPORTED_REPORT        = _TAG(NS_DAV, 'supported-report')
TIMEOUT                 = _TAG(NS_DAV, 'timeout')
UNAUTHENTICATED         = _TAG(NS_DAV, 'unauthenticated')
WRITE                   = _TAG(NS_DAV, 'write')

# Sync tags
LIMIT                   = _TAG(NS_DAV, 'limit')
NUM_RESULTS             = _TAG(NS_DAV, 'nresults')
SYNC_COLLECTION         = _TAG(NS_DAV, 'sync-collection')
SYNC_LEVEL              = _TAG(NS_DAV, 'sync-level')
SYNC_TOKEN              = _TAG(NS_DAV, 'sync-token')

# Error tags
LOCK_TOKEN_REQUEST_URI  = _TAG(NS_DAV, 'lock-token-matches-request-uri')
LOCK_TOKEN_SUBMITTED    = _TAG(NS_DAV, 'lock-token-submitted')
NEED_PRIVILEGES         = _TAG(NS_DAV, 'need-privileges')
NO_ABSTRACT             = _TAG(NS_DAV, 'no-abstract')
NO_ACE_CONFLICT         = _TAG(NS_DAV, 'no-ace-conflict')
NO_CONFLICTING_LOCK     = _TAG(NS_DAV, 'no-conflicting-lock')
NOT_SUPPORTED_PRIVILEGE = _TAG(NS_DAV, 'not-supported-privilege')
RECOGNIZED_PRINCIPAL    = _TAG(NS_DAV, 'recognized-principal')
VALID_RESOURCETYPE      = _TAG(NS_DAV, 'valid-resourcetype')

# Mount tags
MOUNT                   = _TAG(NS_DAVMOUNT, 'mount')
MOUNT_URL               = _TAG(NS_DAVMOUNT, 'url')
MOUNT_OPEN              = _TAG(NS_DAVMOUNT, 'open')
MOUNT_USERNAME          = _TAG(NS_DAVMOUNT, 'username')

# ACL tags
ACL_ALL                 = _ACL(NS_DAV, 'all')
ACL_BIND                = _ACL(NS_DAV, 'bind')
ACL_READ                = _ACL(NS_DAV, 'read')
ACL_READ_ACL            = _ACL(NS_DAV, 'read-acl')
ACL_READ_CUR_USER_PSET  = _ACL(NS_DAV, 'read-current-user-privilege-set')
ACL_UNBIND              = _ACL(NS_DAV, 'unbind')
ACL_UNLOCK              = _ACL(NS_DAV, 'unlock')
ACL_WRITE               = _ACL(NS_DAV, 'write')
ACL_WRITE_ACL           = _ACL(NS_DAV, 'write-acl')
ACL_WRITE_CONTENT       = _ACL(NS_DAV, 'write-content')
ACL_WRITE_PROPERTIES    = _ACL(NS_DAV, 'write-properties')

# Attributes
#ATTR_DT                 = _ATTR(NS_MSXMLDATA, 'dt')
ATTR_LANG               = _ATTR(NS_XML, 'lang')

DEFAULT_PROPS = frozenset((
	CONTENT_LENGTH,
	CONTENT_TYPE,
	ETAG,
	LAST_MODIFIED,
	QUOTA_AVAIL_BYTES,
	QUOTA_USED_BYTES,
	RESOURCE_TYPE
))

RO_PROPS = frozenset(STANDARD_PROPS)

