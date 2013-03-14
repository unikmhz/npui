from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import json
from netprofile.ext.direct import JsonReprEncoder

def jsone(data):
	return json.dumps(data, cls=JsonReprEncoder, indent=3)

