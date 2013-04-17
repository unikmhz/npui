#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from lxml import etree

NS_DAV = 'DAV:'
NS_NETPROFILE = 'http://netprofile.ru/ns/dav/'
NS_APACHE = 'http://apache.org/dav/props/'

CN_DAV = '{DAV:}'
CN_NETPROFILE = '{http://netprofile.ru/ns/dav/}'
CN_APACHE = '{http://apache.org/dav/props/}'

NS_MAP = {
	'd'  : NS_DAV,
	'ap' : NS_APACHE,
	'np' : NS_NETPROFILE
}

ACL                     = CN_DAV + 'acl'
ACL_RESTRICTIONS        = CN_DAV + 'acl-restrictions'
CONTENT_LENGTH          = CN_DAV + 'getcontentlength'
CONTENT_TYPE            = CN_DAV + 'getcontenttype'
CREATION_DATE           = CN_DAV + 'creationdate'
CUR_USER_PRIVILEGE_SET  = CN_DAV + 'current-user-privilege-set'
DISPLAY_NAME            = CN_DAV + 'displayname'
ETAG                    = CN_DAV + 'getetag'
EXECUTABLE              = CN_APACHE + 'executable'
INHERITED_ACL_SET       = CN_DAV + 'inherited-acl-set'
LAST_MODIFIED           = CN_DAV + 'getlastmodified'
LOCK_DISCOVERY          = CN_DAV + 'lockdiscovery'
QUOTA_AVAIL_BYTES       = CN_DAV + 'quota-available-bytes'
QUOTA_USED_BYTES        = CN_DAV + 'quota-used-bytes'
RESOURCE_TYPE           = CN_DAV + 'resourcetype'
SUPPORTED_LOCK          = CN_DAV + 'supportedlock'
SUPPORTED_PRIVILEGE_SET = CN_DAV + 'supported-privilege-set'
SUPPORTED_REPORT_SET    = CN_DAV + 'supported-report-set'

COLLECTION              = CN_DAV + 'collection'
PRINCIPAL               = CN_DAV + 'principal'

ERROR                   = CN_DAV + 'error'
HREF                    = CN_DAV + 'href'
MKCOL                   = CN_DAV + 'mkcol'
MULTISTATUS             = CN_DAV + 'multistatus'
PROP                    = CN_DAV + 'prop'
PROPFIND                = CN_DAV + 'propfind'
PROPSTAT                = CN_DAV + 'propstat'
RESPONSE                = CN_DAV + 'response'
SET                     = CN_DAV + 'set'
STATUS                  = CN_DAV + 'status'

SUPPORTED_REPORT        = CN_DAV + 'supported-report'
VALID_RESOURCETYPE      = CN_DAV + 'valid-resourcetype'

DEFAULT_PROPS = frozenset((
	CONTENT_LENGTH,
	CONTENT_TYPE,
	ETAG,
	LAST_MODIFIED,
	QUOTA_AVAIL_BYTES,
	QUOTA_USED_BYTES,
	RESOURCE_TYPE
))

