import json
from netprofile.ext.direct import JsonReprEncoder

def jsone(data):
	return json.dumps(data, cls=JsonReprEncoder, indent=3)

