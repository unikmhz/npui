from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from itertools import groupby
from sqlalchemy.orm import attributes

def populate_related(parents, id_key, res_key, reltype, subq, flt=None, relid_key='id'):
	ids = []
	for p in parents:
		if callable(flt) and not flt(p):
			continue
		keyval = getattr(p, id_key, None)
		if keyval and (keyval not in ids):
			ids.append(keyval)
	if len(ids) > 0:
		for rel in subq.filter(getattr(reltype, relid_key).in_(ids)):
			for p in parents:
				if callable(flt) and not flt(p):
					continue
				keyval = getattr(p, id_key, None)
				if keyval and (keyval == getattr(rel, relid_key)):
					attributes.set_committed_value(p, res_key, rel)

def populate_related_list(parents, id_key, res_key, reltype, subq, flt=None, relid_key='id'):
	ids = []
	for p in parents:
		if callable(flt) and not flt(p):
			continue
		keyval = getattr(p, id_key, None)
		if keyval and (keyval not in ids):
			ids.append(keyval)
	if len(ids) > 0:
		ch = dict((k, list(v)) for k, v in groupby(
			subq.filter(getattr(reltype, relid_key).in_(ids)),
			lambda c: getattr(c, relid_key)
		))
	for p in parents:
		if callable(flt) and not flt(p):
			continue
		keyval = getattr(p, id_key, None)
		if keyval:
			attributes.set_committed_value(p, res_key, ch.get(keyval, ()))

