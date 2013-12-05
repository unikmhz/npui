from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from netprofile_entities import Address
#тут кое-что поменялось, появился модуль access, откуда теперь надо брать AccessEntity
from netprofile_access import models
from netprofile_core import User
from netprofile_stashes import Stash
from netprofile_rates import Rate
from netprofile_dialup import IPPool
from netprofile_ipaddresses import IPv4Address
from netprofile_ipaddresses import IPv6Address
from netprofile_hosts import Host
from netprofile_networks import Network
from netprofile_devices import Device
AccessEntity = models.AccessEntity
from netprofile.common.cache import cache
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


