from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from sqlalchemy.orm import (
	scoped_session,
	sessionmaker
)
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import event

DBSession = scoped_session(sessionmaker(
	extension=ZopeTransactionExtension()
))
Base = declarative_base()

