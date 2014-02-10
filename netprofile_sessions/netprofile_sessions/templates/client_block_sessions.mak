## -*- coding: utf-8 -*-

					<li><a title="${_('Show currently active sessions of this user', domain='netprofile_sessions')}" href="${req.route_url('stashes.cl.accounts', traverse=(stash.id, 'sessions', a.id, 'active'))}">${_('Active Sessions', domain='netprofile_sessions')}</a></li>
					<li><a title="${_('Show past sessions of this user', domain='netprofile_sessions')}" href="${req.route_url('stashes.cl.accounts', traverse=(stash.id, 'sessions', a.id, 'past'))}">${_('Past Sessions', domain='netprofile_sessions')}</a></li>
