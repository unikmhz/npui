from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
	'Entity',
	'EntityFlag',
	'EntityFlagType',
	'EntityState',
	'PhysicalEntity',
	'LegalEntity',
	'StructuralEntity',
	'ExternalEntity'
]

from sqlalchemy import (
	Column,
	Date,
	FetchedValue,
	ForeignKey,
	Index,
	Numeric,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	func,
	text,
	or_
)

from sqlalchemy.orm import (
	backref,
	contains_eager,
	joinedload,
	relationship
)

from sqlalchemy.ext.associationproxy import association_proxy

#from colanderalchemy import (
#	Column,
#	relationship
#)

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIString,
	DeclEnum,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	UInt64,
	npbool
)
from netprofile.db.ddl import Comment
from netprofile.db.util import (
	populate_related,
	populate_related_list
)
from netprofile.ext.columns import (
	HybridColumn,
	MarkupColumn
)
from netprofile_geo.models import (
	District,
	House,
	Street
)
from netprofile_geo.filters import AddressFilter

from pyramid.threadlocal import get_current_request
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_entities')

class EntityType(DeclEnum):
	"""
	Entity type ENUM.
	"""
	physical   = 'physical',   _('Physical'),   10
	legal      = 'legal',      _('Legal'),      20
	structural = 'structural', _('Structural'), 30
	external   = 'external',   _('External'),   40
	access     = 'access',     _('Access'),     50

class Entity(Base):
	"""
	Base NetProfile entity type.
	"""

	@classmethod
	def _filter_address(cls, query, value):
		if not isinstance(value, dict):
			return query
		if 'houseid' in value:
			val = int(value['houseid'])
			if val > 0:
				query = query.filter(or_(
					PhysicalEntity.house_id == val,
					LegalEntity.house_id == val,
					StructuralEntity.house_id == val
				))
		elif 'streetid' in value:
			val = int(value['streetid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).filter(House.street_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(or_(
						PhysicalEntity.house_id.in_(val),
						LegalEntity.house_id.in_(val),
						StructuralEntity.house_id.in_(val)
					))
		elif 'districtid' in value:
			val = int(value['districtid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).join(Street).filter(Street.district_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(or_(
						PhysicalEntity.house_id.in_(val),
						LegalEntity.house_id.in_(val),
						StructuralEntity.house_id.in_(val)
					))
		elif 'cityid' in value:
			val = int(value['cityid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).join(Street).join(District).filter(District.city_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(or_(
						PhysicalEntity.house_id.in_(val),
						LegalEntity.house_id.in_(val),
						StructuralEntity.house_id.in_(val)
					))
		return query

	__tablename__ = 'entities_def'
	__table_args__ = (
		Comment('Entities'),
		Index('entities_def_i_parentid', 'parentid'),
		Index('entities_def_i_cby', 'cby'),
		Index('entities_def_i_mby', 'mby'),
		Index('entities_def_i_esid', 'esid'),
		Index('entities_def_i_nick', 'nick'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_CREATE',
				'cap_edit'      : 'ENTITIES_EDIT',
				'cap_delete'    : 'ENTITIES_DELETE',

				'tree_property' : 'children',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('Entities'),
				'menu_order'    : 10,
				'default_sort'  : (),
				'grid_view'     : (
					'nick',
					MarkupColumn(
						name='object',
						header_string=_('Object'),
						template="""
{__str__}
<tpl if="data.flags && data.flags.length">
	<br />
	<tpl for="data.flags">
		<img class="np-inline-img" src="/static/entities/img/flags/{0}.png" alt="{1}" />
	</tpl>
</tpl>
"""
					),
					HybridColumn(
						'data',
						header_string=_('Information'),
						template="""
<tpl if="data.house || data.address">
	<img class="np-inline-img" src="/static/entities/img/house_small.png" />
	{data.address} {data.house} {data.entrance} {data.floor} {data.flat}
</tpl>
<tpl if="data.phone_home || data.phone_work || data.phone_cell || data.cp_phone_work || data.cp_phone_cell">
<tpl if="data.house || data.address"><br /></tpl>
<tpl if="data.phone_home">
	<img class="np-inline-img" src="/static/entities/img/phone_small.png" />
	{data.phone_home}
</tpl>
<tpl if="data.phone_work">
	<img class="np-inline-img" src="/static/entities/img/phone_small.png" />
	{data.phone_work}
</tpl>
<tpl if="data.phone_cell">
	<img class="np-inline-img" src="/static/entities/img/mobile_small.png" />
	{data.phone_cell}
</tpl>
<tpl if="data.cp_phone_work">
	<img class="np-inline-img" src="/static/entities/img/phone_small.png" />
	{data.cp_phone_work}
</tpl>
<tpl if="data.cp_phone_cell">
	<img class="np-inline-img" src="/static/entities/img/mobile_small.png" />
	{data.cp_phone_cell}
</tpl>
</tpl>
"""
					),
					'state'
				),
				'easy_search'   : ('nick',),
				'detail_pane'   : ('netprofile_entities.views', 'dpane_entities'),
				'extra_search'  : (
					AddressFilter('address', _filter_address,
						title=_('Address')
					),
				),
			}
		}
	)
	id = Column(
		'entityid',
		UInt32(),
		Sequence('entityid_seq'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	parent_id = Column(
		'parentid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_def_fk_parentid', onupdate='CASCADE'),
		Comment('Parent entity ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Parent'),
			'filter_type'   : 'none'
		}
	)
	nick = Column(
		Unicode(255),
		Comment('Entity nickname'),
		nullable=False,
		info={
			'header_string' : _('Name')
#			'column_xtype'  : 'treecolumn'
		}
	)
	state_id = Column(
		'esid',
		UInt32(),
		ForeignKey('entities_states.esid', name='entities_def_fk_esid', onupdate='CASCADE'),
		Comment('Entity state ID'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('State'),
			'filter_type'   : 'list'
		}
	)
	relative_dn = Column(
		'rdn',
		Unicode(255),
		Comment('Entity LDAP relative distinguished name'),
		nullable=False,
		info={
			'header_string' : _('LDAP RDN')
		}
	)
	type = Column(
		'etype',
		EntityType.db_type(),
		Comment('Entity type'),
		nullable=False,
		default=EntityType.physical,
		server_default=EntityType.physical,
		info={
			'header_string' : _('Type')
		}
	)
	creation_time = Column(
		'ctime',
		TIMESTAMP(),
		Comment('Creation timestamp'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Created')
		}
	)
	modification_time = Column(
		'mtime',
		TIMESTAMP(),
		Comment('Last modification timestamp'),
		nullable=False,
#		default=zzz,
		server_default=func.current_timestamp(),
		server_onupdate=func.current_timestamp(),
		info={
			'header_string' : _('Modified')
		}
	)
	created_by_id = Column(
		'cby',
		UInt32(),
		ForeignKey('users.uid', name='entities_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Created by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Created')
		}
	)
	modified_by_id = Column(
		'mby',
		UInt32(),
		ForeignKey('users.uid', name='entities_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Modified by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Modified')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Entity description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : 'entity',
		'polymorphic_on'       : type,
		'with_polymorphic'     : '*'
	}

	state = relationship(
		'EntityState',
		innerjoin=True,
		backref='entities'
	)
	children = relationship(
		'Entity',
		backref=backref('parent', remote_side=[id])
	)
	created_by = relationship(
		'User',
		foreign_keys=created_by_id,
		backref='created_entities'
	)
	modified_by = relationship(
		'User',
		foreign_keys=modified_by_id,
		backref='modified_entities'
	)
	flagmap = relationship(
		'EntityFlag',
		backref=backref('entity', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	flags = association_proxy(
		'flagmap',
		'type',
		creator=lambda v: EntityFlag(type=v)
	)

	@classmethod
	def __augment_result__(cls, sess, res, params):
		populate_related(
			res, 'house_id', 'house', House,
			sess.query(House).options(joinedload(House.street)),
			lambda e: isinstance(e, (PhysicalEntity, LegalEntity, StructuralEntity))
		)
		populate_related(
			res, 'state_id', 'state', EntityState,
			sess.query(EntityState)
		)
		populate_related_list(
			res, 'id', 'flagmap', EntityFlag,
			sess.query(EntityFlag),
			None, 'entity_id'
		)
		return res

	@property
	def data(self):
		return {
			'flags' : [(ft.id, ft.name) for ft in self.flags]
		}

	def __str__(self):
		return '%s' % str(self.nick)

class EntityState(Base):
	"""
	NetProfile entity state.
	"""
	__tablename__ = 'entities_states'
	__table_args__ = (
		Comment('Entity states'),
		Index('entities_states_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ENTITIES',
				'cap_read'     : 'ENTITIES_LIST',
				'cap_create'   : 'ENTITIES_STATES_CREATE',
				'cap_edit'     : 'ENTITIES_STATES_EDIT',
				'cap_delete'   : 'ENTITIES_STATES_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : _('Entity States'),
				'menu_order'   : 10,
				'default_sort' : (),
				'grid_view'    : ('name',),
				'form_view'    : ('name', 'descr'),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'esid',
		UInt32(),
		Sequence('esid_seq'),
		Comment('Entity state ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Entity state name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Entity state description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	def __str__(self):
		return '%s' % str(self.name)

class EntityFlagType(Base):
	__tablename__ = 'entities_flags_types'
	__table_args__ = (
		Comment('Entity flag types'),
		Index('entities_flags_types_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ENTITIES',
				'cap_read'     : 'ENTITIES_LIST',
				'cap_create'   : 'ENTITIES_FLAGTYPES_CREATE',
				'cap_edit'     : 'ENTITIES_FLAGTYPES_EDIT',
				'cap_delete'   : 'ENTITIES_FLAGTYPES_DELETE',

				'show_in_menu' : 'admin',
				'menu_name'    : _('Entity Flags'),
				'menu_order'   : 10,
				'default_sort' : (),
				'grid_view'    : ('name',),
				'form_view'    : ('name', 'descr'),
				'easy_search'  : ('name',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'flagid',
		UInt32(),
		Sequence('flagid_seq'),
		Comment('Entity flag type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Entity flag type name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Entity flag type description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	flagmap = relationship(
		'EntityFlag',
		backref=backref('type', innerjoin=True, lazy='joined'),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	entities = association_proxy(
		'flagmap',
		'entity',
		creator=lambda v: EntityFlag(entity=v)
	)

	def __str__(self):
		return '%s' % str(self.name)

class EntityFlag(Base):
	__tablename__ = 'entities_flags_def'
	__table_args__ = (
		Comment('Entity flag mappings'),
		Index('entities_flags_def_u_ef', 'entityid', 'flagid', unique=True),
		Index('entities_flags_def_i_flagid', 'flagid'),
		{
		}
	)
	id = Column(
		'efid',
		UInt32(),
		Sequence('efid_seq'),
		Comment('Entity flag ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_flags_def_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		nullable=False,
		info={
			'header_string' : _('Entity')
		}
	)
	type_id = Column(
		'flagid',
		UInt32(),
		ForeignKey('entities_flags_types.flagid', name='entities_flags_types_fk_flagid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity flag type ID'),
		nullable=False,
		info={
			'header_string' : _('Type')
		}
	)

class PhysicalEntity(Entity):
	"""
	Physical entity. Describes single individual.
	"""

	@classmethod
	def _filter_address(cls, query, value):
		if not isinstance(value, dict):
			return query
		if 'houseid' in value:
			val = int(value['houseid'])
			if val > 0:
				query = query.filter(PhysicalEntity.house_id == val)
		elif 'streetid' in value:
			val = int(value['streetid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).filter(House.street_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(PhysicalEntity.house_id.in_(val))
		elif 'districtid' in value:
			val = int(value['districtid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).join(Street).filter(Street.district_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(PhysicalEntity.house_id.in_(val))
		elif 'cityid' in value:
			val = int(value['cityid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).join(Street).join(District).filter(District.city_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(PhysicalEntity.house_id.in_(val))
		return query

	__tablename__ = 'entities_physical'
	__table_args__ = (
		Comment('Physical entities'),
		Index('entities_physical_u_contractid', 'contractid', unique=True),
		Index('entities_physical_i_name_family', 'name_family'),
		Index('entities_physical_i_name_given', 'name_given'),
		Index('entities_physical_i_houseid', 'houseid'),
		Index('entities_physical_i_flat', 'flat'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ENTITIES',
				'cap_read'     : 'ENTITIES_LIST',
				'cap_create'   : 'ENTITIES_CREATE',
				'cap_edit'     : 'ENTITIES_EDIT',
				'cap_delete'   : 'ENTITIES_DELETE',

				'show_in_menu' : 'modules',
				'menu_name'    : _('Physical entities'),
				'menu_order'   : 10,
				'menu_parent'  : 'entity',
				'default_sort' : (),
				'grid_view'    : ('nick', 'name_family', 'name_given', 'house', 'floor', 'flat', 'phone_home', 'phone_cell'),
				'form_view'    : (
					'nick', 'state', 'flags', 'contractid',
					'name_family', 'name_given', 'name_middle',
					'house', 'entrance', 'floor', 'flat',
					'phone_home', 'phone_work', 'phone_cell',
					'email', 'icq', 'homepage', 'birthdate',
					'pass_series', 'pass_num', 'pass_issuedate', 'pass_issuedby',
					'descr'
				),
				'easy_search'  : ('nick', 'name_family'),
				'detail_pane'  : ('netprofile_entities.views', 'dpane_entities'),
				'extra_search'  : (
					AddressFilter('address', _filter_address,
						title=_('Address')
					),
				),
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : EntityType.physical
	}
	id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_physical_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	contract_id = Column(
		'contractid',
		UInt32(),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Contract')
		}
	)
	name_family = Column(
		Unicode(255),
		Comment('Family name'),
		nullable=False,
		info={
			'header_string' : _('Family Name')
		}
	)
	name_given = Column(
		Unicode(255),
		Comment('Given name'),
		nullable=False,
		info={
			'header_string' : _('Given Name')
		}
	)
	name_middle = Column(
		Unicode(255),
		Comment('Middle name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Middle Name')
		}
	)
	house_id = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='entities_physical_fk_houseid', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('House'),
			'filter_type'   : 'none'
		}
	)
	entrance = Column(
		UInt8(),
		Comment('Entrance number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entr.')
		}
	)
	floor = Column(
		UInt8(),
		Comment('Floor number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Floor')
		}
	)
	flat = Column(
		UInt16(),
		Comment('Flat number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Flat')
		}
	)
	phone_home = Column(
		Unicode(24),
		Comment('Home phone'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Home Phone')
		}
	)
	phone_work = Column(
		Unicode(24),
		Comment('Work phone'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Work Phone')
		}
	)
	phone_cell = Column(
		Unicode(24),
		Comment('Cell phone'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Cell')
		}
	)
	email = Column(
		Unicode(64),
		Comment('External e-mail'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('E-mail')
		}
	)
	icq = Column(
		Unicode(64),
		Comment('ICQ UIN'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('ICQ')
		}
	)
	homepage = Column(
		Unicode(64),
		Comment('Homepage URL'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('URL')
		}
	)
	birthdate = Column(
		Date(),
		Comment('Birth date'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('DoB')
		}
	)
	passport_series = Column(
		'pass_series',
		Unicode(8),
		Comment('Passport series'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Pass. Series')
		}
	)
	passport_number = Column(
		'pass_num',
		Unicode(8),
		Comment('Passport number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Pass. Number')
		}
	)
	passport_issued_by = Column(
		'pass_issuedby',
		Unicode(255),
		Comment('Passport issued by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Pass. Issue')
		}
	)
	passport_issue_date = Column(
		'pass_issuedate',
		Date(),
		Comment('Passport issue date'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Pass. Issued By')
		}
	)

	house = relationship(
		'House',
		backref='physical_entities'
	)

	@property
	def data(self):
		req = get_current_request()
		loc = get_localizer(req)

		ret = super(PhysicalEntity, self).data
		if self.house:
			ret['house'] = str(self.house)
		if self.entrance:
			ret['entrance'] = '%s %s' % (
				loc.translate(_('entr.')),
				str(self.entrance)
			)
		if self.floor:
			ret['floor'] = '%s %s' % (
				loc.translate(_('fl.')),
				str(self.floor)
			)
		if self.flat:
			ret['flat'] = '%s %s' % (
				loc.translate(_('app.')),
				str(self.flat)
			)
		if self.phone_home:
			ret['phone_home'] = '%s %s' % (
				loc.translate(_('home:')),
				str(self.phone_home)
			)
		if self.phone_work:
			ret['phone_work'] = '%s %s' % (
				loc.translate(_('work:')),
				str(self.phone_work)
			)
		if self.phone_cell:
			ret['phone_cell'] = '%s %s' % (
				loc.translate(_('cell:')),
				str(self.phone_cell)
			)
		return ret

	def __str__(self):
		strs = []
		if self.name_family:
			strs.append(self.name_family)
		if self.name_given:
			strs.append(self.name_given)
		if self.name_middle:
			strs.append(self.name_middle)
		return ' '.join(strs)

class LegalEntity(Entity):
	"""
	Legal entity. Describes a company.
	"""

	@classmethod
	def _filter_address(cls, query, value):
		if not isinstance(value, dict):
			return query
		if 'houseid' in value:
			val = int(value['houseid'])
			if val > 0:
				query = query.filter(LegalEntity.house_id == val)
		elif 'streetid' in value:
			val = int(value['streetid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).filter(House.street_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(LegalEntity.house_id.in_(val))
		elif 'districtid' in value:
			val = int(value['districtid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).join(Street).filter(Street.district_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(LegalEntity.house_id.in_(val))
		elif 'cityid' in value:
			val = int(value['cityid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).join(Street).join(District).filter(District.city_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(LegalEntity.house_id.in_(val))
		return query

	__tablename__ = 'entities_legal'
	__table_args__ = (
		Comment('Legal entities'),
		Index('entities_legal_u_name', 'name', unique=True),
		Index('entities_legal_u_contractid', 'contractid', unique=True),
		Index('entities_legal_i_houseid', 'houseid'),
		Index('entities_legal_i_flat', 'flat'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ENTITIES',
				'cap_read'     : 'ENTITIES_LIST',
				'cap_create'   : 'ENTITIES_CREATE',
				'cap_edit'     : 'ENTITIES_EDIT',
				'cap_delete'   : 'ENTITIES_DELETE',

				'show_in_menu' : 'modules',
				'menu_name'    : _('Legal entities'),
				'menu_order'   : 20,
				'menu_parent'  : 'entity',
				'default_sort' : (),
				'grid_view'    : ('nick', 'name', 'cp_name_family', 'cp_name_given', 'house', 'floor', 'flat', 'cp_phone_work', 'cp_phone_cell'),
				'form_view'    : (
					'nick', 'state', 'flags', 'contractid',
					'name',
					'cp_name_family', 'cp_name_given', 'cp_name_middle', 'cp_title',
					'house', 'entrance', 'floor', 'flat',
					'cp_phone_work', 'cp_phone_cell', 'phone_rec', 'phone_fax',
					'cp_email', 'cp_icq', 'homepage', 'address_legal',
					'props_inn', 'props_kpp', 'props_bic', 'props_rs', 'props_cs', 'props_bank',
					'descr'
				),
				'easy_search'  : ('nick', 'name'),
				'detail_pane'  : ('netprofile_entities.views', 'dpane_entities'),
				'extra_search'  : (
					AddressFilter('address', _filter_address,
						title=_('Address')
					),
				),
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : EntityType.legal
	}
	id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_legal_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	contract_id = Column(
		'contractid',
		UInt32(),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Contract')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Legal name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	house_id = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='entities_legal_fk_houseid', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('House'),
			'filter_type'   : 'none'
		}
	)
	entrance = Column(
		UInt8(),
		Comment('Entrance number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entr.')
		}
	)
	floor = Column(
		UInt8(),
		Comment('Floor number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Floor')
		}
	)
	flat = Column(
		UInt16(),
		Comment('Flat number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Flat')
		}
	)
	contact_name_family = Column(
		'cp_name_family',
		Unicode(255),
		Comment('Contact person - family name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Family Name')
		}
	)
	contact_name_given = Column(
		'cp_name_given',
		Unicode(255),
		Comment('Contact person - given name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Given Name')
		}
	)
	contact_name_middle = Column(
		'cp_name_middle',
		Unicode(255),
		Comment('Contact person - middle name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Middle Name')
		}
	)
	contact_title = Column(
		'cp_title',
		Unicode(255),
		Comment('Contact person - title'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Title')
		}
	)
	contact_phone_work = Column(
		'cp_phone_work',
		Unicode(24),
		Comment('Contact person - work phone'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Work Phone')
		}
	)
	contact_phone_cell = Column(
		'cp_phone_cell',
		Unicode(24),
		Comment('Contact person - cell phone'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Cell')
		}
	)
	contact_email = Column(
		'cp_email',
		Unicode(64),
		Comment('Contact person - e-mail'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('E-mail')
		}
	)
	contact_icq = Column(
		'cp_icq',
		Unicode(64),
		Comment('Contact person - ICQ UIN'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('ICQ')
		}
	)
	phone_reception = Column(
		'phone_rec',
		Unicode(64),
		Comment('Reception phone number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Rec.')
		}
	)
	phone_fax = Column(
		Unicode(64),
		Comment('Facsimile number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Fax')
		}
	)
	homepage = Column(
		Unicode(64),
		Comment('Homepage URL'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('URL')
		}
	)
	address_legal = Column(
		Unicode(255),
		Comment('Legal address'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Legal Addr.')
		}
	)
	props_inn = Column(
		Unicode(64),
		Comment('Properties - INN'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Taxpayer ID')
		}
	)
	props_kpp = Column(
		Unicode(64),
		Comment('Properties - KPP'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Tax Code')
		}
	)
	props_bic = Column(
		Unicode(64),
		Comment('Properties - BIC'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Bank ID')
		}
	)
	props_rs = Column(
		Unicode(64),
		Comment('Properties - R/S'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Acc. #')
		}
	)
	props_cs = Column(
		Unicode(64),
		Comment('Properties - C/S'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('C./acc. #')
		}
	)
	props_bank = Column(
		Unicode(255),
		Comment('Properties - bank'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Bank')
		}
	)

	house = relationship(
		'House',
		backref='legal_entities'
	)

	@property
	def data(self):
		req = get_current_request()
		loc = get_localizer(req)

		ret = super(LegalEntity, self).data
		if self.house:
			ret['house'] = str(self.house)
		if self.entrance:
			ret['entrance'] = '%s %s' % (
				loc.translate(_('entr.')),
				str(self.entrance)
			)
		if self.floor:
			ret['floor'] = '%s %s' % (
				loc.translate(_('fl.')),
				str(self.floor)
			)
		if self.flat:
			ret['flat'] = '%s %s' % (
				loc.translate(_('app.')),
				str(self.flat)
			)
		if self.contact_phone_work:
			ret['cp_phone_work'] = '%s %s' % (
				loc.translate(_('work:')),
				str(self.contact_phone_work)
			)
		if self.contact_phone_cell:
			ret['cp_phone_cell'] = '%s %s' % (
				loc.translate(_('cell:')),
				str(self.contact_phone_cell)
			)
		return ret

	def __str__(self):
		return str(self.name)

class StructuralEntity(Entity):
	"""
	Structural entity. Describes a building.
	"""

	@classmethod
	def _filter_address(cls, query, value):
		if not isinstance(value, dict):
			return query
		if 'houseid' in value:
			val = int(value['houseid'])
			if val > 0:
				query = query.filter(StructuralEntity.house_id == val)
		elif 'streetid' in value:
			val = int(value['streetid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).filter(House.street_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(StructuralEntity.house_id.in_(val))
		elif 'districtid' in value:
			val = int(value['districtid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).join(Street).filter(Street.district_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(StructuralEntity.house_id.in_(val))
		elif 'cityid' in value:
			val = int(value['cityid'])
			if val > 0:
				sess = DBSession()
				sq = sess.query(House).join(Street).join(District).filter(District.city_id == val)
				val = [h.id for h in sq]
				if len(val) > 0:
					query = query.filter(StructuralEntity.house_id.in_(val))
		return query

	__tablename__ = 'entities_structural'
	__table_args__ = (
		Comment('Structural entities'),
		Index('entities_structural_i_houseid', 'houseid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ENTITIES',
				'cap_read'     : 'ENTITIES_LIST',
				'cap_create'   : 'ENTITIES_CREATE',
				'cap_edit'     : 'ENTITIES_EDIT',
				'cap_delete'   : 'ENTITIES_DELETE',

				'show_in_menu' : 'modules',
				'menu_name'    : _('Structural entities'),
				'menu_order'   : 30,
				'menu_parent'  : 'entity',
				'default_sort' : (),
				'grid_view'    : ('nick', 'house'),
				'form_view'    : ('nick', 'state', 'flags', 'house', 'descr'),
				'easy_search'  : ('nick',),
				'detail_pane'  : ('netprofile_entities.views', 'dpane_entities'),
				'extra_search'  : (
					AddressFilter('address', _filter_address,
						title=_('Address')
					),
				),
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : EntityType.structural
	}
	id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_structural_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	house_id = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='entities_structural_fk_houseid', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=False,
		info={
			'header_string' : _('House'),
			'filter_type'   : 'none'
		}
	)

	house = relationship(
		'House',
		backref='structural_entities'
	)

	@property
	def data(self):
		ret = super(StructuralEntity, self).data
		if self.house:
			ret['house'] = str(self.house)
		return ret

	def __str__(self):
		return str(self.house)

class ExternalEntity(Entity):
	"""
	External entity. Describes an object outside of geo database.
	"""

	__tablename__ = 'entities_external'
	__table_args__ = (
		Comment('External entities'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ENTITIES',
				'cap_read'     : 'ENTITIES_LIST',
				'cap_create'   : 'ENTITIES_CREATE',
				'cap_edit'     : 'ENTITIES_EDIT',
				'cap_delete'   : 'ENTITIES_DELETE',

				'show_in_menu' : 'modules',
				'menu_name'    : _('External entities'),
				'menu_order'   : 40,
				'menu_parent'  : 'entity',
				'default_sort' : (),
				'grid_view'    : ('nick', 'name', 'address'),
				'form_view'    : (
					'nick', 'state', 'flags',
					'name', 'address', 'descr'
				),
				'easy_search'  : ('nick', 'name'),
				'detail_pane'  : ('netprofile_entities.views', 'dpane_entities')
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : EntityType.external
	}
	id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_external_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Entity name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	address = Column(
		Unicode(255),
		Comment('Entity address'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Address')
		}
	)

	@property
	def data(self):
		ret = super(ExternalEntity, self).data
		if self.address:
			ret['address'] = str(self.address)
		return ret

	def __str__(self):
		return str(self.name)

# FIXME: needs own module
class AccessEntity(Entity):
	__tablename__ = 'entities_access'
	__table_args__ = (
		Comment('Access entities'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_ENTITIES',
				'cap_read'     : 'ENTITIES_LIST',
				'cap_create'   : 'ENTITIES_CREATE',
				'cap_edit'     : 'ENTITIES_EDIT',
				'cap_delete'   : 'ENTITIES_DELETE',

				'show_in_menu' : 'modules',
				'menu_name'    : _('Access entities'),
				'menu_order'   : 50,
				'menu_parent'  : 'entity',
				'default_sort' : (),
#				'grid_view'    : ('SUXX',),
#				'easy_search'  : ('SUXX',),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : EntityType.access
	}
	id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_access_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	password = Column(
		Unicode(255),
		Comment('Cleartext password'),
		nullable=False,
		info={
			'header_string' : _('Password'),
			'secret_value'  : True,
			'editor_xtype'  : 'passwordfield'
		}
	)
	stash_id = Column(
		'stashid',
		UInt32(),
		# FKEY
		Comment('Used stash ID'),
		nullable=False,
		info={
			'header_string' : _('Stash')
		}
	)
	rate_id = Column(
		'rateid',
		UInt32(),
		# FKEY
		Comment('Used rate ID'),
		nullable=False,
		info={
			'header_string' : _('Rate')
		}
	)
	alias_id = Column(
		'aliasid',
		UInt32(),
		ForeignKey('entities_access.entityid', name='entities_access_fk_aliasid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Aliased access entity ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Alias Of')
		}
	)
	next_rate_id = Column(
		'nextrateid',
		UInt32(),
		# FKEY
		Comment('Next rate ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Next Rate')
		}
	)
	ipv4_address_id = Column(
		'ipaddrid',
		UInt32(),
		# FKEY
		Comment('IPv4 address ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv4 Address')
		}
	)
	ipv6_address_id = Column(
		'ip6addrid',
		UInt64(),
		# FKEY
		Comment('IPv6 address ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv6 Address')
		}
	)
	used_traffic_ingress = Column(
		'ut_ingress',
		Numeric(16, 0),
		Comment('Used ingress traffic'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Ingress')
		}
	)
	used_traffic_egress = Column(
		'ut_egress',
		Numeric(16, 0),
		Comment('Used egress traffic'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Egress')
		}
	)
	used_seconds = Column(
		'u_sec',
		UInt32(),
		Comment('Used seconds'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Seconds')
		}
	)
	quota_period_end = Column(
		'qpend',
		TIMESTAMP(),
		Comment('End of quota period'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Ends')
		}
	)
	access_state = Column(
		'state',
		UInt8(),
		Comment('Access code'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Access Code')
		}
	)
	policy_ingress = Column(
		'pol_ingress',
		ASCIIString(255),
		Comment('Ingress traffic policy'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Ingress Policy')
		}
	)
	policy_egress = Column(
		'pol_egress',
		ASCIIString(255),
		Comment('Egress traffic policy'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Egress Policy')
		}
	)
	check_block_state = Column(
		'bcheck',
		NPBoolean(),
		Comment('Check block state'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Check Blocks')
		}
	)
	check_paid_services = Column(
		'pcheck',
		NPBoolean(),
		Comment('Check paid services'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Check Services')
		}
	)

