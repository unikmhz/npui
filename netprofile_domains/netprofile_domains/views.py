from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)
from netprofile.common.hooks import register_hook

_ = TranslationStringFactory('netprofile_domain')

@register_hook('core.dpanetabs.domains.Domain')
def _dpane_domain_aliases(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'          : loc.translate(_('Aliases')),
		'xtype'          : 'grid_domains_DomainAlias',
		'stateId'        : None,
		'stateful'       : False,
		'hideColumns'    : (),
		'extraParamProp' : 'domainid'
	})
	tabs.append({
		'title'          : loc.translate(_('TXT Records')),
		'xtype'          : 'grid_domains_DomainTXTRecord',
		'stateId'        : None,
		'stateful'       : False,
		'hideColumns'    : (),
		'extraParamProp' : 'domainid'
	})

