## -*- coding: utf-8 -*-
${_('Hello %s!') % entity.name_given}

${_('You have recently requested a password recovery.')}
% if change_pass:
${_('Your password was automatically changed.')}
${_('Here is your new password:')} ${new_pass}
% elif access.password_plain:
${_('Here is your password:')} ${access.password_plain}
% endif

${_('If you didn\'t request a password recovery please contact support immediately.')}

