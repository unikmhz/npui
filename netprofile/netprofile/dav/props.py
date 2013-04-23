#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from lxml import etree

STANDARD_PROPS = set()

NS_DAV = 'DAV:'
NS_NETPROFILE = 'http://netprofile.ru/ns/dav/'
NS_APACHE = 'http://apache.org/dav/props/'

NS_MAP = {
	'd'  : NS_DAV,
	'ap' : NS_APACHE,
	'np' : NS_NETPROFILE
}

def _TAG(ns, name):
	return '{%s}%s' % (ns, name)

def _ACL(ns, name):
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
CONTENT_LENGTH          = _PROP(NS_DAV, 'getcontentlength')
CONTENT_TYPE            = _PROP(NS_DAV, 'getcontenttype')
CREATION_DATE           = _PROP(NS_DAV, 'creationdate')
CUR_USER_PRIVILEGE_SET  = _PROP(NS_DAV, 'current-user-privilege-set')
DISPLAY_NAME            = _PROP(NS_DAV, 'displayname')
ETAG                    = _PROP(NS_DAV, 'getetag')
EXECUTABLE              = _PROP(NS_APACHE, 'executable')
INHERITED_ACL_SET       = _PROP(NS_DAV, 'inherited-acl-set')
LAST_MODIFIED           = _PROP(NS_DAV, 'getlastmodified')
LOCK_DISCOVERY          = _PROP(NS_DAV, 'lockdiscovery')
PRINCIPAL_URL           = _PROP(NS_DAV, 'principal-URL')
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
ACTIVE_LOCK             = _TAG(NS_DAV, 'activelock')
ALL_PROPS               = _TAG(NS_DAV, 'allprop')
DEPTH                   = _TAG(NS_DAV, 'depth')
ERROR                   = _TAG(NS_DAV, 'error')
EXCLUSIVE               = _TAG(NS_DAV, 'exclusive')
EXPAND_PROPERTY         = _TAG(NS_DAV, 'expand-property')
HREF                    = _TAG(NS_DAV, 'href')
INCLUDE                 = _TAG(NS_DAV, 'include')
LOCK_ENTRY              = _TAG(NS_DAV, 'lockentry')
LOCK_ROOT               = _TAG(NS_DAV, 'lockroot')
LOCK_SCOPE              = _TAG(NS_DAV, 'lockscope')
LOCK_TOKEN              = _TAG(NS_DAV, 'locktoken')
LOCK_TYPE               = _TAG(NS_DAV, 'locktype')
MKCOL                   = _TAG(NS_DAV, 'mkcol')
MULTI_STATUS            = _TAG(NS_DAV, 'multistatus')
OWNER                   = _TAG(NS_DAV, 'owner')
PRINC_PROP_SEARCH       = _TAG(NS_DAV, 'principal-property-search')
PRINC_SEARCH_PROP_SET   = _TAG(NS_DAV, 'principal-search-property-set')
PRIVILEGE               = _TAG(NS_DAV, 'privilege')
PROP                    = _TAG(NS_DAV, 'prop')
PROPERTY_UPDATE         = _TAG(NS_DAV, 'propertyupdate')
PROPFIND                = _TAG(NS_DAV, 'propfind')
PROPNAME                = _TAG(NS_DAV, 'propname')
PROPSTAT                = _TAG(NS_DAV, 'propstat')
REMOVE                  = _TAG(NS_DAV, 'remove')
REPORT                  = _TAG(NS_DAV, 'report')
RESOURCE                = _TAG(NS_DAV, 'resource')
RESPONSE                = _TAG(NS_DAV, 'response')
RESPONSE_DESCRIPTION    = _TAG(NS_DAV, 'responsedescription')
SET                     = _TAG(NS_DAV, 'set')
SHARED                  = _TAG(NS_DAV, 'shared')
STATUS                  = _TAG(NS_DAV, 'status')
SUPPORTED_PRIVILEGE     = _TAG(NS_DAV, 'supported-privilege')
SUPPORTED_REPORT        = _TAG(NS_DAV, 'supported-report')
TIMEOUT                 = _TAG(NS_DAV, 'limeout')
WRITE                   = _TAG(NS_DAV, 'write')

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

