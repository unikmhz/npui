def boolean_to_enum(value):
	if value is None:
		return None
	if value == 'FALSE':
		return 'N'
	if value:
		return 'Y'
	return 'N'

def enum_to_boolean(value):
	if value is None:
		return None
	if value == 'Y':
		return True
	return False

