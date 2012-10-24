__all__ = [
	'City',
	'District',
	'Street',
	'House',
	'Place',
	'HouseGroup',
	'HouseGroupMapping'
]

from sqlalchemy import (
	Column,
	ForeignKey,
	Index,
	Sequence,
	Unicode,
	UnicodeText,
	text
)

from sqlalchemy.orm import (
	backref,
	relationship
)

from sqlalchemy.ext.associationproxy import (
	association_proxy
)

#from colanderalchemy import (
#	Column,
#	relationship
#)

from netprofile.db.connection import Base
from netprofile.db.fields import (
	UInt8,
	UInt16,
	UInt32
)
from netprofile.db.ddl import Comment

class City(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_cities'
	__table_args__ = (
		Comment('Cities'),
		Index('addr_cities_u_name', 'name', unique=True),
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
				'easy_search'  : ('name',),
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
		Comment('Contract prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Prefix'
		}
	)

	districts = relationship(
		'District',
		backref=backref('city', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
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
		Index('addr_districts_u_name', 'name', unique=True),
		Index('addr_districts_i_cityid', 'cityid'),
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
				'grid_view'    : ('city', 'name', 'prefix'),
				'easy_search'  : ('name',),
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
	city_id = Column(
		'cityid',
		UInt32(),
		ForeignKey('addr_cities.cityid', name='addr_districts_fk_cityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('City ID'),
		nullable=False,
		info={
			'header_string' : 'City'
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
	prefix = Column(
		Unicode(32),
		Comment('Contract prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Prefix'
		}
	)

	streets = relationship(
		'Street',
		backref=backref('district', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
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
		Index('addr_streets_u_street', 'prefix', 'suffix', 'name', unique=True),
		Index('addr_streets_u_name', 'name', unique=True),
		Index('addr_streets_i_districtid', 'districtid'),
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
				'grid_view'    : ('district', 'name', 'prefix', 'suffix'),
				'easy_search'  : ('name',),
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
	district_id = Column(
		'districtid',
		UInt32(),
		ForeignKey('addr_districts.districtid', name='addr_streets_fk_districtid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('District ID'),
		nullable=False,
		info={
			'header_string' : 'District'
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
	prefix = Column(
		Unicode(8),
		Comment('Street name prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Prefix'
		}
	)
	suffix = Column(
		Unicode(8),
		Comment('Street name suffix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Suffix'
		}
	)

	houses = relationship(
		'House',
		backref=backref('street', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		l = []
		if self.prefix:
			l.append(self.prefix)
		l.append(self.name)
		if self.suffix:
			l.append(self.suffix)
		return ' '.join(l)

class House(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_houses'
	__table_args__ = (
		Comment('Houses'),
		Index('addr_houses_u_house', 'streetid', 'number', 'num_slash', 'num_suffix', 'building', unique=True),
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
				'grid_view'    : ('street', 'number', 'num_slash', 'num_suffix', 'building', 'entrnum', 'postindex'),
				'easy_search'  : ('number',),
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
	street_id = Column(
		'streetid',
		UInt32(),
		ForeignKey('addr_streets.streetid', name='addr_houses_fk_streetid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Street ID'),
		nullable=False,
		info={
			'header_string' : 'Street'
		}
	)
	number = Column(
		UInt16(),
		Comment('House number'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : 'Number'
		}
	)
	building = Column(
		UInt16(),
		Comment('House building'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : 'Building'
		}
	)
	second_number = Column(
		'num_slash',
		UInt16(),
		Comment('Second house number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Second Num.'
		}
	)
	number_suffix = Column(
		'num_suffix',
		Unicode(32),
		Comment('House number suffix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Num. Suffix'
		}
	)
	entrances = Column(
		'entrnum',
		UInt8(),
		Comment('Number of entrances'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : 'Entr. #'
		}
	)
	postal_code = Column(
		'postindex',
		Unicode(8),
		Comment('Postal code'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Postal Code'
		}
	)

	places = relationship(
		'Place',
		backref=backref('house', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	house_groups = relationship(
		'HouseGroupMapping',
		backref=backref('house', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		l = [str(self.street), str(self.number)]
		if self.number_suffix:
			l.append(self.number_suffix)
		if self.second_number:
			l.append('/' + str(self.second_number))
		if self.building:
			l.append(str(self.building))
		return ' '.join(l)

class Place(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_places'
	__table_args__ = (
		Comment('Places'),
		Index('addr_places_u_number', 'number', unique=True),
		Index('addr_places_i_houseid', 'houseid'),
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
				'easy_search'  : ('number',),
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
	house_id = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='addr_places_fk_houseid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=False,
		info={
			'header_string' : 'House'
		}
	)
	number = Column(
		UInt16(),
		Comment('Place number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Number'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Place name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Name'
		}
	)
	entrance = Column(
		UInt8(),
		Comment('Entrance number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Entr. #'
		}
	)
	floor = Column(
		UInt8(),
		Comment('Floor number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : 'Floor #'
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

class HouseGroup(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_hgroups_def'
	__table_args__ = (
		Comment('House groups'),
		Index('addr_hgroups_def_u_name', 'name', unique=True),
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
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)

	id = Column(
		'ahgid',
		UInt32(),
		Sequence('ahgid_seq'),
		Comment('House group ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : 'ID'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Place name'),
		nullable=False,
		info={
			'header_string' : 'Name'
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
	mappings = relationship(
		'HouseGroupMapping',
		backref=backref('group', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	houses = association_proxy(
		'mappings',
		'house'
	)

	def __str__(self):
		return '%s' % str(self.name)

class HouseGroupMapping(Base):
	"""
	TBW
	"""
	__tablename__ = 'addr_hgroups_houses'
	__table_args__ = (
		Comment('House group memberships'),
		Index('addr_hgroups_houses_u_member', 'ahgid', 'houseid', unique=True),
		Index('addr_hgroups_houses_i_houseid', 'houseid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_GEO',
				'cap_read'     : 'GEO_LIST',
				'cap_create'   : 'GEO_CREATE',
				'cap_edit'     : 'GEO_EDIT',
				'cap_delete'   : 'GEO_DELETE',

				'default_sort' : (),
				'grid_view'    : ('group', 'house'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)

	id = Column(
		'ahghid',
		UInt32(),
		Sequence('ahghid_seq'),
		Comment('House group membership ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : 'ID'
		}
	)
	group_id = Column(
		'ahgid',
		UInt32(),
		ForeignKey('addr_hgroups_def.ahgid', name='addr_hgroups_houses_fk_ahgid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('House group ID'),
		nullable=False,
		info={
			'header_string' : 'Group'
		}
	)
	house_id = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='addr_hgroups_houses_fk_houseid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=False,
		info={
			'header_string' : 'House'
		}
	)

