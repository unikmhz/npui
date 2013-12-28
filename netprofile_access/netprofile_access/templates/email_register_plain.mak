## -*- coding: utf-8 -*-
${_('Hello %s!') % entity.name_given}

${_('Thank you for registering an account in our system.')}
${_('Here is your activation link:')}

${req.route_url('access.cl.activate', _query={ 'for' : entity.nick, 'code' : link.value }) | n}

${_('Be sure to follow it before trying to log in.')}

