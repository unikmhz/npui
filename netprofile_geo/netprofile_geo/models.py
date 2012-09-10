__all__ = [
	'City',
	'District',
	'Street',
	'House',
	'Place',
	'HGroup'
]

from sqlalchemy import (
	Boolean,
	CHAR,
	Column,
	DefaultClause,
	FetchedValue,
	ForeignKey,
	Index,
	Integer,
	LargeBinary,
	PickleType,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	func,
	text
)

from sqlalchemy.orm import (
	backref,
	deferred,
	relationship
)

from sqlalchemy.ext.declarative import (
	declarative_base,
	declared_attr
)

from sqlalchemy.ext.associationproxy import (
	association_proxy
)
from sqlalchemy.ext.hybrid import (
	hybrid_property
)
from sqlalchemy.orm.collections import (
	attribute_mapped_collection
)

#from colanderalchemy import (
#	Column,
#	relationship
#)

from netprofile.common.phpserialize import HybridPickler
from netprofile.db.connection import DBSession, Base
from netprofile.db.fields import (
	ASCIIFixedString,
	ASCIIString,
	DeclEnum,
	ExactUnicode,
	IPv4Address,
	IPv6Address,
	NPBoolean,
	UInt8,
	UInt16,
	Int16,
	UInt32,
	npbool
)
from netprofile.db.ddl import Comment

import hashlib

class City(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_cities'
	__table_args__ = (
		Comment('Cities'),
		Index('u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_GEO',
				'cap_read'     : 'GEO_LIST',
				'cap_create'   : 'GEO_CREATE',
				'cap_edit'     : 'GEO_EDIT',
				'cap_delete'   : 'GEO_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : 'Cities',
				'menu_order'   : 40,
				'default_sort' : (),
				'grid_view'    : ('name', 'prefix'),
				'easy_search'  : ('name'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)

	id = Column(
		'cityid',
		UInt32(),
		Sequence('cityid_seq'),
		Comment('City ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : 'ID'
		}
	)
	name = Column(
		Unicode(255),
		Comment('City name'),
		nullable=False,
		info={
			'header_string' : 'Name'
		}
	)
	prefix = Column(
		Unicode(32),
		Comment('Contract Prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Prefix'
		}
	)
	districts = relationship(
		'District',
		backref=backref('city', innerjoin=True)
	)

	def __str__(self):
		return '%s' % str(self.name)

class District(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_districts'
	__table_args__ = (
		Comment('Districts'),
		Index('district_u_name', 'name', unique=True),
		Index('i_cityid', 'cityid', unique=False),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_GEO',
				'cap_read'     : 'GEO_LIST',
				'cap_create'   : 'GEO_CREATE',
				'cap_edit'     : 'GEO_EDIT',
				'cap_delete'   : 'GEO_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : 'Districts',
				'menu_order'   : 50,
				'default_sort' : (),
				'grid_view'    : ('name', 'city', 'prefix'),
				'easy_search'  : ('name'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)

	id = Column(
		'districtid',
		UInt32(),
		Sequence('districtid_seq'),
		Comment('District ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : 'ID'
		}
	)
	name = Column(
		Unicode(255),
		Comment('District name'),
		nullable=False,
		info={
			'header_string' : 'Name'
		}
	)
	cityid = Column(
		'cityid',
		UInt32(),
		ForeignKey('addr_cities.cityid', name='addr_districts_fk_cityid', onupdate='CASCADE'),
		Comment('City ID'),
		nullable=False,
		info={
			'header_string' : 'City'
		}
	)
	prefix = Column(
		Unicode(32),
		Comment('Contract Prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Prefix'
		}
	)
	streets = relationship(
		'Street',
		backref=backref('district', innerjoin=True)
	)

	def __str__(self):
		return '%s' % str(self.name)

class Street(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_streets'
	__table_args__ = (
		Comment('Streets'),
		Index('u_street', 'prefix', 'suffix', 'name', unique=True),
		Index('i_districtid', 'districtid', unique=False),
		Index('u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_GEO',
				'cap_read'     : 'GEO_LIST',
				'cap_create'   : 'GEO_CREATE',
				'cap_edit'     : 'GEO_EDIT',
				'cap_delete'   : 'GEO_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : 'Streets',
				'menu_order'   : 60,
				'default_sort' : (),
				'grid_view'    : ('name', 'district', 'prefix','suffix'),
				'easy_search'  : ('name'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)

	id = Column(
		'streetid',
		UInt32(),
		Sequence('streetid_seq'),
		Comment('Street ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : 'ID'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Street name'),
		nullable=False,
		info={
			'header_string' : 'Name'
		}
	)
	districtid = Column(
		'districtid',
		UInt32(),
		ForeignKey('addr_districts.districtid', name='addr_streets_fk_districtid', onupdate='CASCADE'),
		Comment('District ID'),
		nullable=False,
		info={
			'header_string' : 'District'
		}
	)
	prefix = Column(
		Unicode(8),
		Comment('Street Name Prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Prefix'
		}
	)

	suffix = Column(
		Unicode(8),
		Comment('Street Name Suffix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Suffix'
		}
	)
	houses = relationship(
		'House',
		backref=backref('street', innerjoin=True)
	)

	def __str__(self):
		sn = self.name
		if (self.prefix):
			sn = self.prefix + ' ' + sn
		if (self.suffix):
			sn = sn + ' ' + self.suffix
		return sn

class House(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_houses'
	__table_args__ = (
		Comment('Houses'),
		Index('u_house', 'streetid', 'number', 'building', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_GEO',
				'cap_read'     : 'GEO_LIST',
				'cap_create'   : 'GEO_CREATE',
				'cap_edit'     : 'GEO_EDIT',
				'cap_delete'   : 'GEO_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : 'Houses',
				'menu_order'   : 70,
				'default_sort' : (),
				'grid_view'    : ('street', 'number', 'building', 'num_slash', 'num_suffix', 'entrnum', 'postindex'),
				'easy_search'  : ('number'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)

	id = Column(
		'houseid',
		UInt32(),
		Sequence('houseid_seq'),
		Comment('House ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : 'ID'
		}
	)
	streetid = Column(
		'streetid',
		UInt32(),
		ForeignKey('addr_streets.streetid', name='addr_houses_fk_streetid', onupdate='CASCADE'),
		Comment('Street ID'),
		nullable=False,
		info={
			'header_string' : 'Street'
		}
	)
	number = Column(
		UInt16(),
		Comment('House Number'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : 'Number'
		}
	)
	building = Column(
		UInt16(),
		Comment('House Building'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : 'Building'
		}
	)
	num_slash = Column(
		UInt16(),
		Comment(''),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Number Slash'
		}
	)
	num_suffix = Column(
		Unicode(32),
		Comment(''),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Number Suffix'
		}
	)
	entrnum = Column(
		UInt8(),
		Comment('Entrance Quantity'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : 'Enterance Q'
		}
	)
	postindex = Column(
		Unicode(8),
		Comment('Postal Index'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Index'
		}
	)
	places = relationship(
		'Place',
		backref=backref('house', innerjoin=True)
	)
	hgroups = relationship(
		'HGroupM',
		backref=backref('house', innerjoin=True)
	)

	def __str__(self):
		hn = '1';
		hn = str(self.street) + ' ' + str(self.number)
		if(self.num_suffix):
			hn = hn + self.num_suffix
		if(self.num_slash):
			hn = hn + '/' + str(self.num_slash)
		if(self.building):
			hn = hn + ' ' + str(self.building)
		return hn;

class Place(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_places'
	__table_args__ = (
		Comment('Places'),
		Index('u_number', 'number', unique=True),
		Index('i_houseid', 'houseid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_GEO',
				'cap_read'     : 'GEO_LIST',
				'cap_create'   : 'GEO_CREATE',
				'cap_edit'     : 'GEO_EDIT',
				'cap_delete'   : 'GEO_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : 'Places',
				'menu_order'   : 80,
				'default_sort' : (),
				'grid_view'    : ('house', 'number', 'name', 'entrance', 'floor', 'descr'),
				'easy_search'  : ('number'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)

	id = Column(
		'placeid',
		UInt32(),
		Sequence('placeid_seq'),
		Comment('Place ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : 'ID'
		}
	)
	houseid = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='addr_place_fk_houseid', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=False,
		info={
			'header_string' : 'Street'
		}
	)
	number = Column(
		UInt16(),
		Comment('Place Number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Number'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Place Name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Place Name'
		}
	)
	entrance = Column(
		UInt8(),
		Comment('Entrance Number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Enterance Number'
		}
	)
	floor = Column(
		UInt8(),
		Comment('Floor Number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Floor Number'
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Place description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Description'
		}
	)

	def __str__(self):
		return '%s' % str(self.number)

class HGroup(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_hgroups_def'
	__table_args__ = (
		Comment('House Groups'),
		Index('u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_GEO',
				'cap_read'     : 'GEO_LIST',
				'cap_create'   : 'GEO_CREATE',
				'cap_edit'     : 'GEO_EDIT',
				'cap_delete'   : 'GEO_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : 'House Groups',
				'menu_order'   : 90,
				'default_sort' : (),
				'grid_view'    : ('name', 'descr'),
				'easy_search'  : ('name'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)

	id = Column(
		'ahgid',
		UInt32(),
		Sequence('ahgid_seq'),
		Comment('House Group ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : 'ID'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Place Name'),
		nullable=False,
		info={
			'header_string' : 'Group Name'
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Place description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Description'
		}
	)
	hgroups = relationship(
		'HGroupM',
		backref=backref('hgroup', innerjoin=True)
	)
	privileges = association_proxy(
		'hgroups',
		'house'
	)

	def __str__(self):
		return '%s' % str(self.name)

class HGroupM(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_hgroups_houses'
	__table_args__ = (
		Comment('House Group Memberships'),
		Index('u_member', 'houseid', 'ahgid', unique=True),
		Index('i_houseid', 'houseid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_GEO',
				'cap_read'     : 'GEO_LIST',
				'cap_create'   : 'GEO_CREATE',
				'cap_edit'     : 'GEO_EDIT',
				'cap_delete'   : 'GEO_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : 'House Group Membership',
				'menu_order'   : 91,
				'default_sort' : (),
				'grid_view'    : ('hgroup', 'house'),
#				'easy_search'  : ('name'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)

	id = Column(
		'ahghid',
		UInt32(),
		Sequence('ahghid_seq'),
		Comment('House Group ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : 'ID'
		}
	)
	ahgid = Column(
		'ahgid',
		UInt32(),
		ForeignKey('addr_hgroups_def.ahgid', name='addr_hgroups_houses_fk_ahgid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('House Group ID'),
		nullable=False,
		info={
			'header_string' : 'House Group'
		}
	)
	houseid = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='addr_hgroups_houses_fk_houseid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=False,
		info={
			'header_string' : 'House ID'
		}
	)

