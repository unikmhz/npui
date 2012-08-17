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

def _db_set_cred(sess, tr, conn):
	sess.execute('SET @accessuid = 0')
	sess.execute('SET @accessgid = 0')
	sess.execute('SET @accesslogin = \'[GUEST]\'')

event.listen(DBSession, 'after_begin', _db_set_cred)

