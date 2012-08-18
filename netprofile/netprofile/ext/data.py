from collections import OrderedDict

from sqlalchemy import (
	BigInteger,
	Boolean,
	Date,
	DateTime,
	Float,
	Integer,
	LargeBinary,
	Numeric,
	PickleType,
	SmallInteger,
	String,
	Text,
	Time,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	func,
	or_
)

from netprofile.db.fields import (
	ASCIIString,
	ASCIIFixedString,
	DeclEnumType,
	ExactUnicode,
	Int8,
	Int16,
	Int32,
	Int64,
	IPv4Address,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	UInt64
)

from netprofile.db.connection import (
	Base,
	DBSession
)

from pyramid.security import (
	Allow,
	Deny,
	Everyone,
	Authenticated
)

_INTEGER_SET = (
	Int8,
	Int16,
	Int32,
	Int64,
	Integer,
	UInt8,
	UInt16,
	UInt32,
	UInt64
)

_FLOAT_SET = (
	Numeric
)

_STRING_SET = (
	ASCIIString,
	ASCIIFixedString,
	DeclEnumType,
	ExactUnicode,
	String
)

_BOOLEAN_SET = (
	Boolean,
	NPBoolean
)

_DATE_SET = (
	Date,
	DateTime,
	Time,
	TIMESTAMP
)

_COLUMN_XTYPE_MAP = {
	BigInteger   : 'numbercolumn',
	Boolean      : 'checkcolumn',
	DeclEnumType : 'enumcolumn',
	Float        : 'numbercolumn',
	Int8         : 'numbercolumn',
	Int16        : 'numbercolumn',
	Int32        : 'numbercolumn',
	Int64        : 'numbercolumn',
	Integer      : 'numbercolumn',
	NPBoolean    : 'checkcolumn',
	Numeric      : 'numbercolumn',
	SmallInteger : 'numbercolumn',
	TIMESTAMP    : 'datecolumn',
	UInt8        : 'numbercolumn',
	UInt16       : 'numbercolumn',
	UInt32       : 'numbercolumn',
	UInt64       : 'numbercolumn'
}

_EDITOR_XTYPE_MAP = {
	BigInteger   : 'numberfield',
	Boolean      : 'checkbox',
	Date         : 'datefield',
	DateTime     : 'datefield',
	DeclEnumType : 'combobox',
	Float        : 'numberfield',
	Int8         : 'numberfield',
	Int16        : 'numberfield',
	Int32        : 'numberfield',
	Int64        : 'numberfield',
	Integer      : 'numberfield',
	NPBoolean    : 'checkbox',
	Numeric      : 'numberfield',
	SmallInteger : 'numberfield',
	TIMESTAMP    : 'datefield',
	UInt8        : 'numberfield',
	UInt16       : 'numberfield',
	UInt32       : 'numberfield',
	UInt64       : 'numberfield'
}

_JS_TYPE_MAP = {
	BigInteger   : 'int',
	Boolean      : 'boolean',
	Date         : 'date',
	DateTime     : 'date',
	Float        : 'float',
	NPBoolean    : 'boolean',
	Numeric      : 'float', # ?
	Int8         : 'int',
	Int16        : 'int',
	Int32        : 'int',
	Int64        : 'int',
	Integer      : 'int',
	SmallInteger : 'int',
	TIMESTAMP    : 'date',
	UInt8        : 'int',
	UInt16       : 'int',
	UInt32       : 'int',
	UInt64       : 'int'
}

_DATE_FMT_MAP = {
	Date      : 'Y-m-d',
	DateTime  : 'c',
	Time      : 'H:i:s',
	TIMESTAMP : 'c'
}

def _table_to_class(tname):
	for cname, cls in Base._decl_class_registry.items():
		if getattr(cls, '__tablename__', None) == tname:
			return cls
	raise KeyError(tname)

class ExtColumn(object):
	MIN_PIXELS = 40
	MAX_PIXELS = 300
	DEFAULT_PIXELS = 200

	def __init__(self, sqla_column):
		self.column = sqla_column

	@property
	def name(self):
		return self.column.name

	@property
	def __name__(self):
		return self.name

	@property
	def header_string(self):
		try:
			return self.column.info['header_string']
		except KeyError:
			return self.column.doc

	@property
	def help_text(self):
		try:
			return self.column.info['help_text']
		except KeyError:
			return None

	@property
	def length(self):
		try:
			return self.column.type.length
		except AttributeError:
			return None

	@property
	def pixels(self):
		pix = getattr(self.column.type, 'length', 0)
		if pix > 0:
			pix *= 5
			pix = max(pix, self.MIN_PIXELS)
			pix = min(pix, self.MAX_PIXELS)
		else:
			pix = self.DEFAULT_PIXELS
		return pix

	@property
	def default(self):
		dv = getattr(self.column, 'default', None)
		if dv is not None:
			return dv.arg
		return None

	@property
	def column_xtype(self):
		cls = self.column.type.__class__
		if cls in _COLUMN_XTYPE_MAP:
			return _COLUMN_XTYPE_MAP[cls]
		return None

	@property
	def editor_xtype(self):
		cls = self.column.type.__class__
		if cls in _EDITOR_XTYPE_MAP:
			return _EDITOR_XTYPE_MAP[cls]
		return 'textfield'

	@property
	def js_type(self):
		cls = self.column.type.__class__
		if cls in _JS_TYPE_MAP:
			return _JS_TYPE_MAP[cls]
		return 'string'

	@property
	def secret_value(self):
		try:
			return self.column.info['secret_value']
		except KeyError:
			return False

	def __getattr__(self, attr):
		return getattr(self.column, attr)

	def parse_param(self, param):
		typecls = self.column.type.__class__
		if param is None:
			return None
		if issubclass(typecls, _BOOLEAN_SET):
			return bool(param)
		if issubclass(typecls, _FLOAT_SET):
			return float(param)
		if typecls is DeclEnumType:
			return self.column.type.enum.from_string(param.strip())
		return param

	def get_model_validations(self):
		typecls = self.column.type.__class__
		ret = {}
		if not self.nullable:
			ret['presence'] = True
		if issubclass(typecls, _INTEGER_SET):
			rng = {}
			vmin = getattr(typecls, 'MIN_VALUE')
			vmax = getattr(typecls, 'MAX_VALUE')
			if vmax is None:
				if issubclass(typecls, SmallInteger):
					if getattr(self.column.type, 'unsigned', False):
						vmin = UInt16.MIN_VALUE
						vmax = UInt16.MAX_VALUE
					else:
						vmin = Int16.MIN_VALUE
						vmax = Int16.MAX_VALUE
				elif issubclass(typecls, Integer):
					if getattr(self.column.type, 'unsigned', False):
						vmin = UInt32.MIN_VALUE
						vmax = UInt32.MAX_VALUE
					else:
						vmin = Int32.MIN_VALUE
						vmax = Int32.MAX_VALUE
			if vmin is not None:
				rng['min'] = vmin
			if vmax is not None:
				rng['max'] = vmax
			if len(rng) > 0:
				ret['range'] = rng
		if issubclass(typecls, _STRING_SET):
			ll = {}
			val = self.length
			if val is not None:
				ll['max'] = val
			if not self.nullable:
				ll['min'] = 1
			if len(ll) > 0:
				ret['length'] = ll
		if typecls is DeclEnumType:
			ret['inclusion'] = { 'list' : self.column.type.enum.values() }
		return ret

	def get_editor_cfg(self, initval=None, in_form=False):
		if self.column.primary_key: # add check for read-only non-pk fields
			return {
				'xtype'    : 'hidden',
				'disabled' : True,
				'editable' : False,
				'name'     : self.name
			}
		conf = {
			'xtype'      : self.editor_xtype,
			'allowBlank' : self.nullable,
			'name'       : self.name
		}
		typecls = self.column.type.__class__
		val = self.default
		if initval is not None:
			conf['value'] = initval
		elif (val is not None) or (self.nullable):
			conf['value'] = val
		val = self.help_text
		if val is not None:
			conf['emptyText'] = val
		if issubclass(typecls, _BOOLEAN_SET):
			conf.update({
				'cls'  : 'x-grid-checkheader-editor'
			})
			val = self.default
			if isinstance(val, bool) and val:
				conf['checked'] = True
			elif initval is True:
				conf['checked'] = True
		elif issubclass(typecls, _FLOAT_SET):
			conf.update({
				'style' : 'text-align:right',
				'width' : 50
			})
		elif typecls is DeclEnumType:
			chx = []
			for sym in self.column.type.enum:
				chx.append({
					'id'    : sym.value,
					'value' : sym.description
				})
			conf.update({
				'format'         : 'string',
				'displayField'   : 'value',
				'hiddenName'     : self.name,
				'valueField'     : 'id',
				'mode'           : 'local',
				'triggerAction'  : 'all',
				'editable'       : False,
				'forceSelection' : True,
				'store'          : {
					'xtype'  : 'simplestore',
					'fields' : ['id', 'value'],
					'data'   : chx
				}
			})
		if len(self.column.foreign_keys) > 0:
			fk = self.column.foreign_keys.copy().pop()
			cls = _table_to_class(fk.column.table.name)
			conf.update({
				'xtype'     : 'modelselect',
				'apiModule' : cls.__moddef__,
				'apiClass'  : cls.__name__
			})
		if in_form:
			conf['fieldLabel'] = self.header_string
			val = self.pixels
			if val is not None:
				conf['width'] = val
		return conf

	def get_reader_cfg(self):
		typecls = self.column.type.__class__
		conf = {
			'name'       : self.name,
			'allowBlank' : self.nullable,
			'useNull'    : self.nullable,
			'type'       : self.js_type
		}
		if conf['type'] == 'date':
			conf['dateFormat'] = _DATE_FMT_MAP[typecls]
		val = self.default
		if val is not None:
			if type(val) in {int, str, list, dict, bool}:
				conf['defaultValue'] = val
		return conf

	def get_column_cfg(self):
		if self.secret_value:
			return None
		conf = {
			'header'     : self.header_string,
			'tooltip'    : self.header_string,
			'name'       : self.name,
			'sortable'   : True,
			'filterable' : True,
			'dataIndex'  : self.name,
			'editor'     : self.get_editor_cfg()
		}
		typecls = self.column.type.__class__
		xt = self.column_xtype
		if xt is not None:
			conf['xtype'] = xt
		# add col width?
		if issubclass(typecls, _FLOAT_SET):
			conf.update({
				'align'  : 'right',
				'format' : '0.00'
			})
		if issubclass(typecls, _INTEGER_SET):
			conf.update({
				'format' : '0'
			})
		if issubclass(typecls, _DATE_SET):
			conf.update({
				'format' : _DATE_FMT_MAP[typecls]
			})
		if typecls is DeclEnumType:
			chx = {}
			chf = []
			for sym in self.column.type.enum:
				chx[sym.value] = sym.description
				chf.append({ 'id' : sym.value, 'value' : sym.description })
			conf['valueMap'] = chx
			conf['filter'] = {
				'type'       : 'list',
				'options'    : chf,
				'labelField' : 'value'
			}
		return conf

	def get_related_cfg(self):
		fks = self.column.foreign_keys
		if len(fks) == 0:
			return None
		conf = []
		for fk in fks:
			cls = _table_to_class(fk.column.table.name)
			conf.append({
				'type'       : 'belongsTo',
				'model'      : 'NetProfile.model.%s.%s' % (
					cls.__moddef__,
					cls.__name__
				),
				'foreignKey' : self.name,
				'primaryKey' : fk.column.name
			})
		return conf

	def append_data(self, obj):
		return None

class ExtRelationshipColumn(ExtColumn):
	def __init__(self, sqla_prop):
		self.prop = sqla_prop
		self.column = sqla_prop.local_side[0]

	@property
	def column_xtype(self):
		return None

	def append_data(self, obj):
		k = self.prop.key
		return {
			k : str(getattr(obj, k))
		}

	def get_column_cfg(self):
		conf = super(ExtRelationshipColumn, self).get_column_cfg()
		conf['dataIndex'] = self.prop.key
		return conf

	def get_reader_cfg(self):
		return {
			'name'       : self.prop.key,
			'allowBlank' : self.nullable,
			'useNull'    : self.nullable,
			'type'       : 'string',
			'persist'    : False
		}

class ExtModel(object):
	def __init__(self, sqla_model):
		self.model = sqla_model

	@property
	def name(self):
		return self.model.__name__

	@property
	def __name__(self):
		return self.name

	@property
	def pk(self):
		pkcon = getattr(self.model.__table__, 'primary_key', None)
		if pkcon is None:
			return None
		for col in pkcon:
			return col.name
		return None

	@property
	def easy_search(self):
		return self.model.__table__.info.get('easy_search', [])

	@property
	def show_in_menu(self):
		return self.model.__table__.info.get('show_in_menu', False)

	@property
	def menu_name(self):
		return self.model.__table__.info.get('menu_name', self.model.__name__)

	@property
	def menu_order(self):
		return self.model.__table__.info.get('menu_order', 10)

	@property
	def cap_menu(self):
		return self.model.__table__.info.get('cap_menu')

	@property
	def cap_read(self):
		return self.model.__table__.info.get('cap_read')

	@property
	def cap_create(self):
		return self.model.__table__.info.get('cap_create')

	@property
	def cap_edit(self):
		return self.model.__table__.info.get('cap_edit')

	@property
	def cap_delete(self):
		return self.model.__table__.info.get('cap_delete')

	def get_column(self, colname):
		cols = self.model.__table__.columns
		if colname in cols:
			return ExtColumn(cols[colname])
		prop = self.model.__mapper__.get_property(colname)
		return ExtRelationshipColumn(prop)

	def get_columns(self):
		ret = OrderedDict()
		cols = self.model.__table__.columns
		for ck in cols.keys():
			ret[ck] = ExtColumn(cols[ck])
		return ret

	def get_read_columns(self):
		ret = OrderedDict()
		cols = self.model.__table__.columns.keys()
		try:
			gcols = self.model.__table__.info['grid_view']
			for col in gcols:
				if col in cols:
					continue
				cols.append(col)
		except KeyError:
			pass
		pk = self.pk
		if pk not in cols:
			ret[pk] = self.get_column(pk)
		for col in cols:
			ret[col] = self.get_column(col)
		return ret

	def get_column_cfg(self):
		ret = []
		try:
			cols = self.model.__table__.info['grid_view']
		except KeyError:
			cols = self.model.__table__.columns.keys()
		for col in cols:
			cdef = self.get_column(col).get_column_cfg()
			if cdef is not None:
				ret.append(cdef)
		return ret

	def get_reader_cfg(self):
		ret = []
		for cname, col in self.get_read_columns().items():
			ret.append(col.get_reader_cfg())
		return ret

	def get_related_cfg(self):
		ret = []
		for cname, col in self.get_columns().items():
			colrel = col.get_related_cfg()
			if colrel is not None:
				ret.extend(colrel)
		return ret

	def get_model_validations(self):
		ret = []
		for cname, col in self.get_read_columns().items():
			if isinstance(col, ExtRelationshipColumn):
				continue
			v = col.get_model_validations()
			# <- INSERT CUSTOM VALIDATORS HERE
			for vkey, vdata in v.items():
				vitem = {
					'field' : cname,
					'type'  : vkey
				}
				if isinstance(vdata, dict):
					vitem.update(vdata)
				ret.append(vitem)
		return ret

	def _apply_pagination(self, query, trans, params):
		if '__start' in params:
			val = int(params['__start'])
			if val > 0:
				query = query.offset(val)
		if '__limit' in params:
			val = int(params['__limit'])
			if val > 0:
				query = query.limit(val)
		return query

	def _apply_sorting(self, query, trans, params):
		slist = params['__sort']
		if not isinstance(slist, list):
			return query
		for sdef in slist:
			if (not isinstance(sdef, dict)) or (len(sdef) != 2):
				continue
			if sdef['property'] not in trans:
				continue
			prop = getattr(self.model, trans[sdef['property']].key)
			if sdef['direction'] == 'DESC':
				prop = prop.desc()
			query = query.order_by(prop)
		return query

	def _apply_sstr(self, query, trans, params):
		fields = self.easy_search
		if not isinstance(fields, list):
			return query
		sstr = params['__sstr']
		cond = []
		for f in fields:
			prop = trans[f]
			coldef = self.model.__table__.c[f]
			col = getattr(self.model, prop.key)
			if issubclass(coldef.type.__class__, _STRING_SET):
				cond.append(col.contains(sstr))
		if len(cond) > 0:
			query = query.filter(or_(*cond))
		return query

	def _apply_filters(self, query, trans, params):
		flist = params['__filter']
		for fcol in flist:
			if fcol in trans:
				prop = trans[fcol]
				coldef = self.model.__table__.c[fcol]
				col = getattr(self.model, prop.key)
				filters = flist[fcol]
				for fkey, fval in filters.items():
					if fkey == 'eq':
						query = query.filter(col == fval)
						continue
					if fkey == 'ne':
						query = query.filter(col != fval)
						continue
					if isinstance(fval, list):
						if fkey == 'in':
							query = query.filter(col.in_(fval))
							continue
						if fkey == 'notin':
							query = query.filter(not col.in_(fval))
							continue
					if issubclass(coldef.type.__class__, _INTEGER_SET) or issubclass(coldef.type.__class__, _FLOAT_SET):
						if fkey == 'gt':
							query = query.filter(col > fval)
							continue
						if fkey == 'lt':
							query = query.filter(col < fval)
							continue
						if fkey == 'ge':
							query = query.filter(col >= fval)
							continue
						if fkey == 'le':
							query = query.filter(col <= fval)
							continue
					if issubclass(coldef.type.__class__, _STRING_SET):
						if fkey == 'contains':
							query = query.filter(col.contains(fval))
							continue
						if fkey == 'ncontains':
							query = query.filter(not col.contains(fval))
							continue
						if fkey == 'startswith':
							query = query.filter(col.startswith(fval))
							continue
						if fkey == 'nstartswith':
							query = query.filter(not col.startswith(fval))
							continue
						if fkey == 'endswith':
							query = query.filter(col.endswith(fval))
							continue
						if fkey == 'nendswith':
							query = query.filter(not col.endswith(fval))
							continue
		return query

	def read(self, params, request):
		print('DO READ ON %s' % self.name)
		print(repr(params))
		res = {
			'records' : [],
			'success' : True,
			'total'   : 0
		}
		trans = {}
		records = []
		tot = 0
		cols = self.get_read_columns()
		for cname, col in cols.items():
			trans[cname] = self.model.__mapper__.get_property_by_column(
					col.column)
		sess = DBSession()
		# Cache total?
		q = sess.query(func.count('*')).select_from(self.model)
		if '__filter' in params:
			q = self._apply_filters(q, trans, params)
		if '__sstr' in params:
			q = self._apply_sstr(q, trans, params)
		tot = q.scalar()
		q = sess.query(self.model)
		if '__filter' in params:
			q = self._apply_filters(q, trans, params)
		if '__sstr' in params:
			q = self._apply_sstr(q, trans, params)
		if '__sort' in params:
			q = self._apply_sorting(q, trans, params)
		q = self._apply_pagination(q, trans, params)
		for obj in q:
			row = {}
			for cname, col in cols.items():
				if col.secret_value:
					continue
				if trans[cname].deferred:
					continue
				if isinstance(col, ExtRelationshipColumn):
					extra = col.append_data(obj)
					if extra is not None:
						row.update(extra)
				else:
					row[cname] = getattr(obj, trans[cname].key)
			records.append(row)
		res['records'] = records
		res['total'] = tot
		return res

	def read_one(self, params, request):
		print('DO READ ONE ON %s' % self.name)
		print(repr(params))

	def create(self, params, request):
		print('DO CREATE ON %s' % self.name)
		print(repr(params))
		res = {
			'records' : [],
			'success' : True,
			'total'   : 0
		}
		trans = {}
		cols = self.get_columns()
		rcols = self.get_read_columns()
		for cname, col in rcols.items():
			trans[cname] = self.model.__mapper__.get_property_by_column(
					col.column)

		sess = DBSession()

		for pt in params['records']:
			p = self.pk
			if p in pt:
				del pt[p]
			obj = self.model()
			for p in pt:
				if p not in cols:
					continue
				setattr(obj, trans[p].key, cols[p].parse_param(pt[p]))
			sess.add(obj)
			p = {}
			if '_clid' in pt:
				p['_clid'] = pt['_clid']
			pt = p
			for cname, col in rcols.items():
				if col.secret_value:
					continue
				if trans[cname].deferred:
					continue
				if isinstance(col, ExtRelationshipColumn):
					extra = col.append_data(obj)
					if extra is not None:
						pt.update(extra)
				else:
					pt[cname] = getattr(obj, trans[cname].key)
			res['records'].append(pt)
			res['total'] += 1
		return res

	def update(self, params, request):
		print('DO UPDATE ON %s' % self.name)
		print(repr(params))
		res = {
			'records' : [],
			'success' : True,
			'total'   : 0
		}
		trans = {}
		cols = self.get_columns()
		rcols = self.get_read_columns()
		for cname, col in rcols.items():
			trans[cname] = self.model.__mapper__.get_property_by_column(
					col.column)

		sess = DBSession()

		for pt in params['records']:
			if self.pk not in pt:
				raise Exception('Can\'t find primary key in record parameters')
			obj = sess.query(self.model).get(pt[self.pk])
			for p in pt:
				if (p not in cols) or (p == self.pk):
					continue
				setattr(obj, trans[p].key, cols[p].parse_param(pt[p]))
			pt = {}
			for cname, col in rcols.items():
				if col.secret_value:
					continue
				if trans[cname].deferred:
					continue
				if isinstance(col, ExtRelationshipColumn):
					extra = col.append_data(obj)
					if extra is not None:
						pt.update(extra)
				else:
					pt[cname] = getattr(obj, trans[cname].key)
			res['records'].append(pt)
			res['total'] += 1
		return res

	def delete(self, params, request):
		print('DO DELETE ON %s' % self.name)
		print(repr(params))
		res = {
			'success' : True,
			'total'   : 0
		}
		sess = DBSession()
		for pt in params['records']:
			if self.pk not in pt:
				raise Exception('Can\'t find primary key in record parameters')
			obj = sess.query(self.model).get(pt[self.pk])
			sess.delete(obj)
			res['total'] += 1
		return res

	def get_fields(self, request):
		print('DO GET FIELDS ON %s' % self.name)
		fields = []
		for cname, col in self.get_columns().items():
			fdef = col.get_editor_cfg(in_form=True)
			if fdef is not None:
				fields.append(fdef)
		return { 'fields' : fields }

	def get_menu_tree(self, name):
		if self.show_in_menu == name:
			xname = self.name.lower()
			return {
				'id'      : xname,
				'text'    : self.menu_name,
				'order'   : self.menu_order,
				'leaf'    : True,
				'iconCls' : 'ico-mod-%s' % xname,
				'xview'   : 'grid_%s_%s' % (self.__parent__.moddef, self.name)
			}

class ExtModuleBrowser(object):
	def __init__(self, mmgr, moddef):
		if moddef not in mmgr.modules:
			raise KeyError('Unknown module: \'%s\'')
		self.mmgr = mmgr
		self.moddef = moddef

	@property
	def __name__(self):
		return self.moddef

	def __getitem__(self, name):
		sqla_model = self.mmgr.models[self.moddef][name]
		mod = ExtModel(sqla_model)
		mod.__parent__ = self
		return mod

	def __iter__(self):
		return iter(self.mmgr.models[self.moddef])

	def get_menu_tree(self, name):
		ch = []
		for model in self:
			em = self[model]
			mt = em.get_menu_tree(name)
			if mt:
				ch.append(mt)
		if len(ch) > 0:
			return {
				'id'       : self.moddef,
				'text'     : self.mmgr.loaded[self.moddef].name,
				'expanded' : True,
				'children' : sorted(ch, key=lambda mt: mt['order']),
				'iconCls'  : 'ico-module'
			}

class ExtBrowser(object):
	def __init__(self, mmgr):
		self.mmgr = mmgr

	def __getitem__(self, moddef):
		modbr = ExtModuleBrowser(self.mmgr, moddef)
		modbr.__parent__ = self
		return modbr

	def __iter__(self):
		return iter(self.mmgr.modules)

	def get_menu_data(self):
		return sorted(self.mmgr.menus.values(), key=lambda m: m.order)

	def get_menu_tree(self, name):
		if name not in self.mmgr.menus:
			raise KeyError('Can\'t find menu \'%s\'' % name)
		menu = []
		for module in self:
			em = self[module]
			mt = em.get_menu_tree(name)
			if mt:
				menu.append(mt)
		return menu

