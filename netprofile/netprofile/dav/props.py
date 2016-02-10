#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV property lists
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

from lxml import etree

STANDARD_PROPS = set()

NS_XML        = 'http://www.w3.org/XML/1998/namespace'
NS_DAV        = 'DAV:'

NS_APPLE_DAV  = 'http://www.apple.com/webdav_fs/props/'
NS_ICAL       = 'http://apple.com/ns/ical/'
NS_INFIT_AB   = 'http://inf-it.com/ns/ab/'
NS_INFIT_DAV  = 'http://inf-it.com/ns/dav/'
NS_NETPROFILE = 'http://netprofile.ru/ns/dav/'
NS_SYNC       = 'http://netprofile.ru/ns/davsync/'
NS_APACHE     = 'http://apache.org/dav/props/'
NS_CALDAV     = 'urn:ietf:params:xml:ns:caldav'
NS_CARDDAV    = 'urn:ietf:params:xml:ns:carddav'
NS_MSSCHEMAS  = 'urn:schemas-microsoft-com:'
NS_MSXMLDATA  = 'urn:uuid:c2f41010-65b3-11d1-a29f-00aa00c14882/'
NS_CS         = 'http://calendarserver.org/ns/'
NS_DAVMOUNT   = 'http://purl.org/NET/webdav/mount'

NS_MAP = {
	'd'  : NS_DAV,
	'dm' : NS_DAVMOUNT,
	'cd' : NS_CALDAV,
	'cr' : NS_CARDDAV,
	'ap' : NS_APACHE,
#	'ic' : NS_ICAL,
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
ACL                      = _PROP(NS_DAV, 'acl')
ACL_RESTRICTIONS         = _PROP(NS_DAV, 'acl-restrictions')
ADDRESS_BOOK_COLOR       = _PROP(NS_INFIT_AB, 'addressbook-color')
ADDRESS_BOOK_DESCRIPTION = _PROP(NS_CARDDAV, 'addressbook-description')
ADDRESS_BOOK_HOME_SET    = _PROP(NS_CARDDAV, 'addressbook-home-set')
ADDRESS_DATA             = _PROP(NS_CARDDAV, 'address-data')
ALTERNATE_URI_SET        = _PROP(NS_DAV, 'alternate-URI-set')
CALENDAR_COLOR           = _PROP(NS_ICAL, 'calendar-color')
CONTENT_LENGTH           = _PROP(NS_DAV, 'getcontentlength')
CONTENT_TYPE             = _PROP(NS_DAV, 'getcontenttype')
CREATION_DATE            = _PROP(NS_DAV, 'creationdate')
CTAG                     = _PROP(NS_CS, 'getctag')
CUR_USER_PRINCIPAL       = _PROP(NS_DAV, 'current-user-principal')
CUR_USER_PRIVILEGE_SET   = _PROP(NS_DAV, 'current-user-privilege-set')
DIRECTORY_GATEWAY        = _PROP(NS_CARDDAV, 'directory-gateway')
DISPLAY_NAME             = _PROP(NS_DAV, 'displayname')
ETAG                     = _PROP(NS_DAV, 'getetag')
EXECUTABLE               = _PROP(NS_APACHE, 'executable')
GROUP                    = _PROP(NS_DAV, 'group')
GROUP_MEMBER_SET         = _PROP(NS_DAV, 'group-member-set')
GROUP_MEMBERSHIP         = _PROP(NS_DAV, 'group-membership')
HEADER_VALUE             = _PROP(NS_INFIT_DAV, 'headervalue')
INHERITED_ACL_SET        = _PROP(NS_DAV, 'inherited-acl-set')
IS_COLLECTION            = _PROP(NS_DAV, 'iscollection')
IS_FOLDER                = _PROP(NS_DAV, 'isFolder')
IS_HIDDEN                = _PROP(NS_DAV, 'ishidden')
LAST_MODIFIED            = _PROP(NS_DAV, 'getlastmodified')
LOCK_DISCOVERY           = _PROP(NS_DAV, 'lockdiscovery')
MAX_RESOURCE_SIZE        = _PROP(NS_CARDDAV, 'max-resource-size')
OWNER                    = _PROP(NS_DAV, 'owner')
PRINCIPAL_ADDRESS        = _PROP(NS_CARDDAV, 'principal-address')
PRINCIPAL_URL            = _PROP(NS_DAV, 'principal-URL')
PRINCIPAL_COLL_SET       = _PROP(NS_DAV, 'principal-collection-set')
QUOTA_AVAIL_BYTES        = _PROP(NS_DAV, 'quota-available-bytes')
QUOTA_USED_BYTES         = _PROP(NS_DAV, 'quota-used-bytes')
RESOURCE_TYPE            = _PROP(NS_DAV, 'resourcetype')
SUPPORTED_ADDRESS_DATA   = _PROP(NS_CARDDAV, 'supported-address-data')
SUPPORTED_COLLSET_CAL    = _PROP(NS_CALDAV, 'supported-collation-set')
SUPPORTED_COLLSET_CARD   = _PROP(NS_CARDDAV, 'supported-collation-set')
SUPPORTED_LIVE_PROP_SET  = _PROP(NS_DAV, 'supported-live-property-set')
SUPPORTED_LOCK           = _PROP(NS_DAV, 'supportedlock')
SUPPORTED_PRIVILEGE_SET  = _PROP(NS_DAV, 'supported-privilege-set')
SUPPORTED_REPORT_SET     = _PROP(NS_DAV, 'supported-report-set')

# Resource type tags
ADDRESS_BOOK             = _TAG(NS_CARDDAV, 'addressbook')
CALENDAR                 = _TAG(NS_CALDAV, 'calendar')
COLLECTION               = _TAG(NS_DAV, 'collection')
DIRECTORY                = _TAG(NS_CARDDAV, 'directory')
PRINCIPAL                = _TAG(NS_DAV, 'principal')

# Generic tags
ABSTRACT                 = _TAG(NS_DAV, 'abstract')
ACE                      = _TAG(NS_DAV, 'ace')
ACL_PRINC_PROP_SET       = _TAG(NS_DAV, 'acl-principal-prop-set')
ACTIVE_LOCK              = _TAG(NS_DAV, 'activelock')
ADDRESS_BOOK_MULTIGET    = _TAG(NS_CARDDAV, 'addressbook-multiget')
ADDRESS_BOOK_QUERY       = _TAG(NS_CARDDAV, 'addressbook-query')
ADDRESS_DATA_TYPE        = _TAG(NS_CARDDAV, 'address-data-type')
ALL_PROPS                = _TAG(NS_DAV, 'allprop')
APPLY_TO_PRINC_COLL_SET  = _TAG(NS_DAV, 'apply-to-principal-collection-set')
AUTHENTICATED            = _TAG(NS_DAV, 'authenticated')
DENY                     = _TAG(NS_DAV, 'deny')
DENY_BEFORE_GRANT        = _TAG(NS_DAV, 'deny-before-grant')
DEPTH                    = _TAG(NS_DAV, 'depth')
DESCRIPTION              = _TAG(NS_DAV, 'description')
ERROR                    = _TAG(NS_DAV, 'error')
EXCLUSIVE                = _TAG(NS_DAV, 'exclusive')
EXPAND_PROPERTY          = _TAG(NS_DAV, 'expand-property')
GRANT                    = _TAG(NS_DAV, 'grant')
GRANT_ONLY               = _TAG(NS_DAV, 'grant-only')
HREF                     = _TAG(NS_DAV, 'href')
INCLUDE                  = _TAG(NS_DAV, 'include')
INHERITED                = _TAG(NS_DAV, 'inherited')
INVERT                   = _TAG(NS_DAV, 'invert')
LIMIT_CARD               = _TAG(NS_CARDDAV, 'limit')
LOCK_ENTRY               = _TAG(NS_DAV, 'lockentry')
LOCK_ROOT                = _TAG(NS_DAV, 'lockroot')
LOCK_SCOPE               = _TAG(NS_DAV, 'lockscope')
LOCK_TOKEN               = _TAG(NS_DAV, 'locktoken')
LOCK_TYPE                = _TAG(NS_DAV, 'locktype')
MATCH                    = _TAG(NS_DAV, 'match')
MKCOL                    = _TAG(NS_DAV, 'mkcol')
MULTI_STATUS             = _TAG(NS_DAV, 'multistatus')
NO_INVERT                = _TAG(NS_DAV, 'no-invert')
PRINC_MATCH              = _TAG(NS_DAV, 'principal-match')
PRINC_PROP               = _TAG(NS_DAV, 'principal-property')
PRINC_PROP_SEARCH        = _TAG(NS_DAV, 'principal-property-search')
PRINC_SEARCH_PROP        = _TAG(NS_DAV, 'principal-search-property')
PRINC_SEARCH_PROP_SET    = _TAG(NS_DAV, 'principal-search-property-set')
PRIVILEGE                = _TAG(NS_DAV, 'privilege')
PROP                     = _TAG(NS_DAV, 'prop')
PROPERTY                 = _TAG(NS_DAV, 'property')
PROPERTY_SEARCH          = _TAG(NS_DAV, 'property-search')
PROPERTY_UPDATE          = _TAG(NS_DAV, 'propertyupdate')
PROPFIND                 = _TAG(NS_DAV, 'propfind')
PROPNAME                 = _TAG(NS_DAV, 'propname')
PROPSTAT                 = _TAG(NS_DAV, 'propstat')
PROTECTED                = _TAG(NS_DAV, 'protected')
REMOVE                   = _TAG(NS_DAV, 'remove')
REPORT                   = _TAG(NS_DAV, 'report')
REQUIRED_PRINCIPAL       = _TAG(NS_DAV, 'required-principal')
RESOURCE                 = _TAG(NS_DAV, 'resource')
RESPONSE                 = _TAG(NS_DAV, 'response')
RESPONSE_DESCRIPTION     = _TAG(NS_DAV, 'responsedescription')
SELF                     = _TAG(NS_DAV, 'self')
SET                      = _TAG(NS_DAV, 'set')
SHARED                   = _TAG(NS_DAV, 'shared')
STATUS                   = _TAG(NS_DAV, 'status')
SUPPORTED_COLL_CAL       = _TAG(NS_CALDAV, 'supported-collation')
SUPPORTED_COLL_CARD      = _TAG(NS_CARDDAV, 'supported-collation')
SUPPORTED_PRIVILEGE      = _TAG(NS_DAV, 'supported-privilege')
SUPPORTED_REPORT         = _TAG(NS_DAV, 'supported-report')
TIMEOUT                  = _TAG(NS_DAV, 'timeout')
UNAUTHENTICATED          = _TAG(NS_DAV, 'unauthenticated')
VCARD_ALL_PROPS          = _TAG(NS_CARDDAV, 'allprop')
VCARD_FILTER             = _TAG(NS_CARDDAV, 'filter')
VCARD_IS_NOT_DEFINED     = _TAG(NS_CARDDAV, 'is-not-defined')
VCARD_PARAM_FILTER       = _TAG(NS_CARDDAV, 'param-filter')
VCARD_PROP               = _TAG(NS_CARDDAV, 'prop')
VCARD_PROP_FILTER        = _TAG(NS_CARDDAV, 'prop-filter')
VCARD_TEXT_MATCH         = _TAG(NS_CARDDAV, 'text-match')
WRITE                    = _TAG(NS_DAV, 'write')

# Sync tags
LIMIT                    = _TAG(NS_DAV, 'limit')
NUM_RESULTS              = _TAG(NS_DAV, 'nresults')
SYNC_COLLECTION          = _TAG(NS_DAV, 'sync-collection')
SYNC_LEVEL               = _TAG(NS_DAV, 'sync-level')
SYNC_TOKEN               = _TAG(NS_DAV, 'sync-token')

# Error tags
ADDRESS_BOOK_COLL_LOC_OK = _TAG(NS_CARDDAV, 'addressbook-collection-location-ok')
CANNOT_MODIFY_PROT_PROP  = _TAG(NS_DAV, 'cannot-modify-protected-property')
LOCK_TOKEN_REQUEST_URI   = _TAG(NS_DAV, 'lock-token-matches-request-uri')
LOCK_TOKEN_SUBMITTED     = _TAG(NS_DAV, 'lock-token-submitted')
NEED_PRIVILEGES          = _TAG(NS_DAV, 'need-privileges')
MATCHES_WITHIN_LIMITS    = _TAG(NS_DAV, 'number-of-matches-within-limits')
NO_ABSTRACT              = _TAG(NS_DAV, 'no-abstract')
NO_ACE_CONFLICT          = _TAG(NS_DAV, 'no-ace-conflict')
NO_CONFLICTING_LOCK      = _TAG(NS_DAV, 'no-conflicting-lock')
NO_UID_CONFLICT          = _TAG(NS_CARDDAV, 'no-uid-conflict')
NOT_SUPPORTED_PRIVILEGE  = _TAG(NS_DAV, 'not-supported-privilege')
RECOGNIZED_PRINCIPAL     = _TAG(NS_DAV, 'recognized-principal')
SUPPORTED_ADDRESS_DATA_CONV = _TAG(NS_CARDDAV, 'supported-address-data-conversion')
SYNC_TRAVERSAL_SUPPORTED = _TAG(NS_DAV, 'sync-traversal-supported')
VALID_ADDRESS_DATA       = _TAG(NS_CARDDAV, 'valid-address-data')
VALID_RESOURCETYPE       = _TAG(NS_DAV, 'valid-resourcetype')
VALID_SYNC_TOKEN         = _TAG(NS_DAV, 'valid-sync-token')
VCARD_SUPPORTED_FILTER   = _TAG(NS_CARDDAV, 'supported-filter')

# Mount tags
MOUNT                    = _TAG(NS_DAVMOUNT, 'mount')
MOUNT_URL                = _TAG(NS_DAVMOUNT, 'url')
MOUNT_OPEN               = _TAG(NS_DAVMOUNT, 'open')
MOUNT_USERNAME           = _TAG(NS_DAVMOUNT, 'username')

# ACL tags
ACL_ALL                  = _ACL(NS_DAV, 'all')
ACL_BIND                 = _ACL(NS_DAV, 'bind')
ACL_READ                 = _ACL(NS_DAV, 'read')
ACL_READ_ACL             = _ACL(NS_DAV, 'read-acl')
ACL_READ_CUR_USER_PSET   = _ACL(NS_DAV, 'read-current-user-privilege-set')
ACL_UNBIND               = _ACL(NS_DAV, 'unbind')
ACL_UNLOCK               = _ACL(NS_DAV, 'unlock')
ACL_WRITE                = _ACL(NS_DAV, 'write')
ACL_WRITE_ACL            = _ACL(NS_DAV, 'write-acl')
ACL_WRITE_CONTENT        = _ACL(NS_DAV, 'write-content')
ACL_WRITE_PROPERTIES     = _ACL(NS_DAV, 'write-properties')

# Attributes
#ATTR_DT                  = _ATTR(NS_MSXMLDATA, 'dt')
ATTR_LANG                = _ATTR(NS_XML, 'lang')

DEFAULT_PROPS = frozenset((
	CONTENT_LENGTH,
	CONTENT_TYPE,
	ETAG,
	LAST_MODIFIED,
	QUOTA_AVAIL_BYTES,
	QUOTA_USED_BYTES,
	RESOURCE_TYPE
))

ALLPROPS_EXEMPT = frozenset((
	ADDRESS_BOOK_DESCRIPTION,
	ADDRESS_BOOK_HOME_SET,
	ADDRESS_DATA,
	DIRECTORY_GATEWAY,
	MAX_RESOURCE_SIZE,
	PRINCIPAL_ADDRESS,
	SUPPORTED_ADDRESS_DATA,
	SUPPORTED_COLLSET_CAL,
	SUPPORTED_COLLSET_CARD,
	SYNC_TOKEN
))

RO_PROPS = frozenset(STANDARD_PROPS)

