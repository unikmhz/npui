#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: TV subscription module - DV Crypt protocol handling
# Copyright © 2017 Alex Unigovsky
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

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

from bitarray import bitarray
import enum
from future.utils import (
    binary_type,
    integer_types,
    raise_from,
    text_type
)
from pyramid.decorator import reify
import socket
from sqlalchemy.orm import joinedload
import struct
from Cryptodome.Hash import MD2

from netprofile.common.crypto import get_salt_bytes
from netprofile_access.models import AccessEntity

MAGIC_SYNC = 0xe25aa5e4
REQUEST_DATA_OFFSET = 12
REPLY_DATA_OFFSET = 12

ADDR_NONE = 0
ADDR_MAX = 0x20
ADDR_ALL = 0xff

DATA_LEN_MAX = 65535
SALT_LEN = 8


@enum.unique
class DVCryptCommand(enum.Enum):
    LOGIN_GETINFO = 0x10
    LOGIN_TRY = 0x11
    LOGOUT = 0x12
    LOGIN_GETVERSION = 0x13

    BUS_GET_STATUS = 0x80
    BUS_STOP = 0x81
    BUS_RESUME = 0x82
    ADD_MODULE = 0x88

    SUBSCRIBER_GET = 0x33
    SUBSCRIBER_SET = 0x34

    STATUS_GET = 0x20
    CFG_GET = 0x21
    SETTINGS_GET = 0x22
    SETTINGS_SET = 0x23
    SETTINGS_RESET = 0x24
    MODULE_CLEAR = 0x35
    MODULE_CHECK = 0x36
    MODULE_CHECK_STOP = 0x37
    MODULE_DELETE = 0x38
    MODULE_RESET = 0x39

    LOGO_READ = 0x26
    LOGO_WRITE = 0x27

    TOTALS_GET = 0x40
    DATA_GET = 0x41
    DATA_SET = 0x42
    DATA_FIND = 0x43
    DATA_EPG_DELETE = 0x44

    ETHERNET_ADD = 0x54
    ETHERNET_ADD_STOP = 0x55


@enum.unique
class DVCryptDataType(enum.Enum):
    PACKAGES = 0x01
    SUBSCRIBERS = 0x03
    LOG = 0x04
    EPG = 0x05


@enum.unique
class DVCryptReplyStatus(enum.Enum):
    OK = 0
    BUSY = 1
    ERROR = 2


@enum.unique
class DVCryptServerStatus(enum.Enum):
    ERRPORT = 0x00
    ACTIVE = 0x01
    STOPPING = 0x02
    STOPPED = 0x03
    ADDING = 0x04


@enum.unique
class DVCryptUpdatePriority(enum.Enum):
    LOW = 0
    HIGH = 1


_STRUCT_FORMAT = {
    DVCryptDataType.SUBSCRIBERS: 'BBB64s64s32s64sHBB16s',
    DVCryptDataType.PACKAGES: '19sB'
}


class DVCryptError(Exception):
    pass


class DataLengthError(ValueError, DVCryptError):
    pass


class InvalidCodeError(ValueError, DVCryptError):
    pass


class InvalidAddressError(ValueError, DVCryptError):
    pass


class InvalidUIDError(ValueError, DVCryptError):
    pass


class DVCryptConnectionError(RuntimeError, DVCryptError):
    pass


class DVCryptServerError(RuntimeError, DVCryptError):
    pass


class DVCryptAuthenticationError(DVCryptServerError):
    pass


class DVCryptServerBusyError(DVCryptServerError):
    pass


class DVCryptConnection(object):
    def __init__(self, **settings):
        self._sock = None
        self._auth_as = None
        self._host = settings.get('host', 'localhost')
        self._port = settings.get('port', 8100) or 8100
        self._enc = settings.get('encoding', 'utf8') or 'utf8'

    def _send_request(self, code, address=ADDR_NONE, data=None):
        if not isinstance(code, DVCryptCommand):
            raise InvalidCodeError('Command code must be of type '
                                   'DVCryptCommand')
        if not isinstance(address, integer_types):
            raise InvalidAddressError('Converter address must be an integer')
        if address < 0 or address > ADDR_MAX and address != ADDR_ALL:
            raise InvalidAddressError('Converter address is invalid')
        if isinstance(data, text_type):
            data = data.encode(self._enc)
        data_len = 0 if data is None else len(data)
        if data_len > DATA_LEN_MAX:
            raise DataLengthError('Supplied command data is too long: %d' %
                                  (data_len,))

        cmduid = get_salt_bytes(4, None)
        sendbuf = bytearray(data_len + REQUEST_DATA_OFFSET)
        struct.pack_into('<LBBH4s',
                         sendbuf, 0,
                         MAGIC_SYNC,
                         code.value,
                         address,
                         data_len,
                         cmduid)
        if data_len:
            struct.pack_into('<%ds' % (data_len,),
                             sendbuf, REQUEST_DATA_OFFSET,
                             data)

        try:
            self._sock.sendall(sendbuf)
        except socket.error as sockerr:
            raise_from(DVCryptConnectionError('Socket error'), sockerr)

        return cmduid

    def _recv_reply(self, code=None, cmduid=None):
        if code is not None and not isinstance(code, DVCryptCommand):
            raise InvalidCodeError('Command code must be of type '
                                   'DVCryptCommand')
        if cmduid is not None:
            if not isinstance(cmduid, binary_type):
                raise InvalidUIDError('Command unique ID must be '
                                      'a binary string')
            if len(cmduid) != 4:
                raise InvalidUIDError('Command unique ID must be 4 bytes')

        recvbuf = bytearray(REPLY_DATA_OFFSET)
        recvmv = memoryview(recvbuf)
        bytes_left = REPLY_DATA_OFFSET

        while bytes_left > 0:
            try:
                recv_bytes = self._sock.recv_into(recvmv, bytes_left)
            except InterruptedError:
                continue
            except socket.error as sockerr:
                raise_from(DVCryptConnectionError('Socket error'), sockerr)
            if not recv_bytes:
                raise DVCryptConnectionError('Server closed the connection')
            bytes_left -= recv_bytes
            if bytes_left > 0:
                recvmv = recvmv[recv_bytes:]

        (magic, recv_code, status,
         data_len, recv_cmduid) = struct.unpack('<IBBH4s', recvbuf)

        if magic != MAGIC_SYNC:
            raise DVCryptConnectionError('Received invalid magic number')

        try:
            status = DVCryptReplyStatus(status)
        except ValueError as err:
            raise_from(
                    DVCryptConnectionError('Received an unknown status reply'),
                    err)

        try:
            recv_code = DVCryptCommand(recv_code)
        except ValueError as err:
            raise_from(
                    DVCryptConnectionError('Received an invalid command code'),
                    err)
        if code is not None and recv_code is not code:
            raise DVCryptConnectionError('Received an unexpected command code')
        if cmduid is not None and recv_cmduid != cmduid:
            raise DVCryptConnectionError('Received an unexpected command UID')

        data = None
        if data_len > 0:
            if data_len > DATA_LEN_MAX:
                raise DVCryptConnectionError('Received oversized reply')

            recvbuf = bytearray(data_len)
            recvmv = memoryview(recvbuf)
            bytes_left = data_len

            while bytes_left > 0:
                try:
                    recv_bytes = self._sock.recv_into(recvmv, bytes_left)
                except InterruptedError:
                    continue
                except socket.error as sockerr:
                    raise_from(DVCryptConnectionError('Socket error'), sockerr)
                if not recv_bytes:
                    raise DVCryptConnectionError(
                            'Server closed the connection')
                bytes_left -= recv_bytes
                if bytes_left > 0:
                    recvmv = recvmv[recv_bytes:]

            data = recvbuf

        return (recv_code, recv_cmduid, status, data)

    def _handle_server_error(self, status):
        if status == DVCryptReplyStatus.BUSY:
            raise DVCryptServerBusyError('Server is busy')
        if status == DVCryptReplyStatus.ERROR:
            raise DVCryptServerError('Unspecified server-side error')
        raise ValueError('Unknown server status reply')

    def _iter_login_getinfo(self, data):
        for data_tuple in struct.iter_unpack('<32s64s', data):
            yield (data_tuple[0].rstrip(b' \0').decode(self._enc),
                   data_tuple[1].rstrip(b' \0').decode(self._enc))

    def open(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self._sock.connect((self._host, self._port))
            except InterruptedError:
                continue
            except socket.error as sockerr:
                raise_from(DVCryptConnectionError('Socket error'), sockerr)
            break

    def close(self):
        if self._sock:
            while True:
                try:
                    self._sock.close()
                except InterruptedError:
                    continue
                except socket.error as sockerr:
                    raise_from(DVCryptConnectionError('Socket error'), sockerr)
                break
            self._sock = None
            self._auth_as = None

    def authenticate(self, username, password):
        # Get our salt, plus a list of server's usernames.
        cmduid = self._send_request(DVCryptCommand.LOGIN_GETINFO)
        _, _, status, data = self._recv_reply(DVCryptCommand.LOGIN_GETINFO,
                                              cmduid)
        if status != DVCryptReplyStatus.OK:
            self._handle_server_error(status)

        # Store our salt from reply.
        salt = data[:SALT_LEN]

        # Check if our username exists.
        info_mv = memoryview(data)[SALT_LEN:]
        for info_user, info_desc in self._iter_login_getinfo(info_mv):
            if info_user == username:
                break
        else:
            raise DVCryptAuthenticationError('Unknown username')
        del info_mv

        # Remember unencoded username on successful auth.
        orig_username = username

        # Properly encode username/password.
        if isinstance(username, text_type):
            username = username.encode(self._enc)
        if isinstance(password, text_type):
            password = password.encode(self._enc)

        # Get hashed password.
        ctx = MD2.new()
        ctx.update(password)
        ctx.update(salt)
        hashed_password = ctx.digest()
        del ctx

        # Format/pad request data.
        data = struct.pack('<32s16s', username, hashed_password)

        # Try to authenticate.
        cmduid = self._send_request(DVCryptCommand.LOGIN_TRY, data=data)
        _, _, status, data = self._recv_reply(DVCryptCommand.LOGIN_TRY,
                                              cmduid)
        if status != DVCryptReplyStatus.OK:
            self._handle_server_error(status)

        # TODO: parse/cache LoginSuccess struct.
        if not data:
            raise DVCryptAuthenticationError('Invalid password')
        self._auth_as = orig_username

    def deauthenticate(self):
        if not self._auth_as:
            return False

        cmduid = self._send_request(DVCryptCommand.LOGOUT)
        status = self._recv_reply(DVCryptCommand.LOGOUT, cmduid)[2]

        if status != DVCryptReplyStatus.OK:
            self._handle_server_error(status)

        self._auth_as = None
        return True

    def get_subscriptions(self, from_id, to_id):
        pass

    def set_subscriptions(self, from_id, to_id, mask,
                          priority=DVCryptUpdatePriority.LOW):

        if not isinstance(priority, DVCryptUpdatePriority):
            priority = DVCryptUpdatePriority(priority)
        if isinstance(mask, bitarray):
            mask = mask.tobytes()

        data = struct.pack('<LLB16s',
                           from_id, to_id,
                           priority.value,
                           mask)
        cmduid = self._send_request(DVCryptCommand.SUBSCRIBER_SET, data=data)
        status = self._recv_reply(DVCryptCommand.SUBSCRIBER_SET, cmduid)[2]

        if status != DVCryptReplyStatus.OK:
            self._handle_server_error(status)

    def _count(self, datatype, subtype=0, date=None):
        data = struct.pack('<BBHBB',
                           datatype.value, subtype,
                           date.year if date else 0,
                           date.month if date else 0,
                           date.day if date else 0)

        cmduid = self._send_request(DVCryptCommand.TOTALS_GET, data=data)
        _, _, status, data = self._recv_reply(DVCryptCommand.TOTALS_GET,
                                              cmduid)

        if status != DVCryptReplyStatus.OK:
            self._handle_server_error(status)

        if data is None or len(data) != 4:
            raise DVCryptServerError('Unable to parse totals count')
        return struct.unpack('<L', data)[0]

    def count_users(self):
        return self._count(DVCryptDataType.SUBSCRIBERS)

    def count_packages(self):
        return self._count(DVCryptDataType.PACKAGES)

    def _get(self, datatype, from_id, to_id, subtype=0, date=None):
        if datatype not in _STRUCT_FORMAT:
            raise NotImplementedError('Chosen data type not supported')
        data = struct.pack('<BLLBHBB',
                           datatype.value, from_id, to_id, subtype,
                           date.year if date else 0,
                           date.month if date else 0,
                           date.day if date else 0)

        cmduid = self._send_request(DVCryptCommand.DATA_GET, data=data)
        _, _, status, data = self._recv_reply(DVCryptCommand.DATA_GET, cmduid)

        if status != DVCryptReplyStatus.OK:
            self._handle_server_error(status)

        struct_fmt = '<' + _STRUCT_FORMAT[datatype]
        if struct.calcsize(struct_fmt) * (to_id - from_id + 1) != len(data):
            raise DVCryptServerError('Server returned truncated/padded data')
        return struct.iter_unpack(struct_fmt, data)

    def get_users(self, from_id, to_id):
        return self._get(DVCryptDataType.SUBSCRIBERS, from_id, to_id)

    def get_packages(self, from_id, to_id):
        return self._get(DVCryptDataType.PACKAGES, from_id, to_id)

    def _set(self, datatype, object_id, data_tuple):
        if datatype not in _STRUCT_FORMAT:
            raise NotImplementedError('Chosen data type not supported')
        data = struct.pack('<BL' + _STRUCT_FORMAT[datatype],
                           datatype.value,
                           object_id, *data_tuple)

        cmduid = self._send_request(DVCryptCommand.DATA_SET, data=data)
        status = self._recv_reply(DVCryptCommand.DATA_SET, cmduid)[2]

        if status != DVCryptReplyStatus.OK:
            self._handle_server_error(status)

    def set_user(self, user_id, data_tuple):
        return self._set(DVCryptDataType.SUBSCRIBERS, user_id, data_tuple)

    def set_package(self, package_id, data_tuple):
        return self._set(DVCryptDataType.PACKAGES, package_id, data_tuple)

    def __enter__(self):
        if not self._sock:
            self.open()
        return self

    def __exit__(self, *args):
        if self._sock:
            self.close()


class DVCryptHandler(object):
    def __init__(self, source):
        self.source = source

    @reify
    def connection(self):
        host = self.source.gateway_host
        if not host:
            raise RuntimeError('Can\'t find host to connect to')
        if len(host.ipv4_addresses):
            addr = str(host.ipv4_addresses[0])
        elif len(host.ipv6_addresses):
            addr = str(host.ipv6_addresses[0])
        else:
            addr = str(host)
        return DVCryptConnection(host=addr,
                                 port=self.source.gateway_port,
                                 encoding=self.source.text_encoding)

    def update_access_entity(self, aent):
        has_active_subs = False
        has_free_subs = False
        sub_mask = bitarray(128, endian='little')
        sub_mask.setall(False)
        furthest_qpend = None

        for tvsub in aent.tv_subscriptions_access:
            if not tvsub.active:
                continue
            try:
                extid = int(tvsub.type.external_id)
            except (TypeError, ValueError):
                continue
            if extid >= 128 or extid < 0:
                continue
            sub_mask[extid] = True
            has_active_subs = True
            if tvsub.paid_service:
                qpend = tvsub.paid_service.quota_period_end
                if furthest_qpend is None or furthest_qpend < qpend:
                    furthest_qpend = qpend
            else:
                has_free_subs = True

        if has_free_subs:
            admin_status = 1  # Always active
        elif has_active_subs:
            admin_status = 0  # Determined by end date
        else:
            admin_status = 2  # Always inactive

        parent = aent.parent
        user_name = str(parent)
        if parent.addresses:
            for addr in parent.addresses:
                if addr.primary:
                    user_address = str(addr)
                    break
            else:
                user_address = str(parent.addresses[0])
        if parent.phones:
            for phone in parent.phones:
                if phone.primary:
                    user_phone = str(phone.number)
                    break
            else:
                user_phone = str(parent.phones[0].number)

        enc = self.source.text_encoding or 'utf8'

        data_tuple = (1,  # "In use" flag
                      0 if has_active_subs else 1,  # "Expired" flag
                      admin_status,
                      user_name.encode(enc),
                      user_address.encode(enc),
                      user_phone.encode(enc),
                      aent.description.encode(enc),
                      furthest_qpend.year if furthest_qpend else 0,
                      furthest_qpend.month if furthest_qpend else 0,
                      furthest_qpend.day if furthest_qpend else 0,
                      sub_mask.tobytes())

        for tvcard in aent.tv_cards:
            try:
                extid = int(tvcard.external_id)
            except (TypeError, ValueError):
                continue
            if tvcard.source == self.source:
                self.connection.set_user(extid, data_tuple)

    def update_all(self, sess):
        for aent in sess.query(AccessEntity).options(
                joinedload(AccessEntity.tv_cards)):
            self.update_access_entity(aent)

    def __enter__(self):
        return self.connection.__enter__()

    def __exit__(self, *args):
        return self.connection.__exit__(*args)
