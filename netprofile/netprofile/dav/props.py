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

def TAG(ns, name):
	return '{%s}%s' % (ns, name)

def PROP(ns, name):
	pn = '{%s}%s' % (ns, name)
	STANDARD_PROPS.add(pn)
	return pn

ACL                     = PROP(NS_DAV, 'acl')
ACL_RESTRICTIONS        = PROP(NS_DAV, 'acl-restrictions')
CONTENT_LENGTH          = PROP(NS_DAV, 'getcontentlength')
CONTENT_TYPE            = PROP(NS_DAV, 'getcontenttype')
CREATION_DATE           = PROP(NS_DAV, 'creationdate')
CUR_USER_PRIVILEGE_SET  = PROP(NS_DAV, 'current-user-privilege-set')
DISPLAY_NAME            = PROP(NS_DAV, 'displayname')
ETAG                    = PROP(NS_DAV, 'getetag')
EXECUTABLE              = PROP(NS_APACHE, 'executable')
INHERITED_ACL_SET       = PROP(NS_DAV, 'inherited-acl-set')
LAST_MODIFIED           = PROP(NS_DAV, 'getlastmodified')
LOCK_DISCOVERY          = PROP(NS_DAV, 'lockdiscovery')
QUOTA_AVAIL_BYTES       = PROP(NS_DAV, 'quota-available-bytes')
QUOTA_USED_BYTES        = PROP(NS_DAV, 'quota-used-bytes')
RESOURCE_TYPE           = PROP(NS_DAV, 'resourcetype')
SUPPORTED_LIVE_PROP_SET = PROP(NS_DAV, 'supported-live-property-set')
SUPPORTED_LOCK          = PROP(NS_DAV, 'supportedlock')
SUPPORTED_PRIVILEGE_SET = PROP(NS_DAV, 'supported-privilege-set')
SUPPORTED_REPORT_SET    = PROP(NS_DAV, 'supported-report-set')

COLLECTION              = TAG(NS_DAV, 'collection')
PRINCIPAL               = TAG(NS_DAV, 'principal')

ACTIVE_LOCK             = TAG(NS_DAV, 'activelock')
ALL_PROPS               = TAG(NS_DAV, 'allprop')
DEPTH                   = TAG(NS_DAV, 'depth')
ERROR                   = TAG(NS_DAV, 'error')
EXCLUSIVE               = TAG(NS_DAV, 'exclusive')
HREF                    = TAG(NS_DAV, 'href')
INCLUDE                 = TAG(NS_DAV, 'include')
LOCK_ROOT               = TAG(NS_DAV, 'lockroot')
LOCK_SCOPE              = TAG(NS_DAV, 'lockscope')
LOCK_TOKEN              = TAG(NS_DAV, 'locktoken')
LOCK_TYPE               = TAG(NS_DAV, 'locktype')
MKCOL                   = TAG(NS_DAV, 'mkcol')
MULTI_STATUS            = TAG(NS_DAV, 'multistatus')
OWNER                   = TAG(NS_DAV, 'owner')
PROP                    = TAG(NS_DAV, 'prop')
PROPERTY_UPDATE         = TAG(NS_DAV, 'propertyupdate')
PROPFIND                = TAG(NS_DAV, 'propfind')
PROPNAME                = TAG(NS_DAV, 'propname')
PROPSTAT                = TAG(NS_DAV, 'propstat')
REMOVE                  = TAG(NS_DAV, 'remove')
RESPONSE                = TAG(NS_DAV, 'response')
RESPONSE_DESCRIPTION    = TAG(NS_DAV, 'responsedescription')
SET                     = TAG(NS_DAV, 'set')
SHARED                  = TAG(NS_DAV, 'shared')
STATUS                  = TAG(NS_DAV, 'status')
TIMEOUT                 = TAG(NS_DAV, 'limeout')
WRITE                   = TAG(NS_DAV, 'write')

LOCK_TOKEN_REQUEST_URI  = TAG(NS_DAV, 'lock-token-matches-request-uri')
LOCK_TOKEN_SUBMITTED    = TAG(NS_DAV, 'lock-token-submitted')
NO_CONFLICTING_LOCK     = TAG(NS_DAV, 'no-conflicting-lock')
SUPPORTED_REPORT        = TAG(NS_DAV, 'supported-report')
VALID_RESOURCETYPE      = TAG(NS_DAV, 'valid-resourcetype')

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

