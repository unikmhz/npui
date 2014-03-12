## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>
% if message:
<div class='bs-callout bs-callout-info'>
<h4>${loc.translate(_("Ready"))}</h4>
<p>${loc.translate(_("Action successfully completed"))}</p>
</div>
% endif

% if vmachines:
  % for m in vmachines:

	 % if m.get('status', None) != 'running':
	    <a role="button" class="btn btn-warning active">
	    <span class="glyphicon glyphicon-fishes"></span>
	    ${m.get('name')}
	    </a>

           <a role="button" class="btn btn-primary" href="/vm?action=start&vmid=${m.get('vmid')}&node=${m.get('node')}&type=${m.get('type')}">
      	   <span class="glyphicon glyphicon-play"></span>
      	   ${loc.translate(_("Start"))}
   	  </a>
           <a role="button" class="btn btn-primary disabled" href="/vm?action=stop&vmid=${m.get('vmid')}&node=${m.get('node')}&type=${m.get('type')}">
     	   <span class="glyphicon glyphicon-stop"></span>
      	   ${loc.translate(_("Stop"))}
   	   </a>

     	 % else:
	    <a role="button" class="btn btn-success active">
	    <span class="glyphicon glyphicon-fishes"></span>
	    ${m.get('name')}
	    </a>

           <a role="button" class="btn btn-primary disabled" href="/vm?action=start&vmid=${m.get('vmid')}&node=${m.get('node')}&type=${m.get('node')}">
      	   <span class="glyphicon glyphicon-play"></span>
      	   ${loc.translate(_("Start"))}
   	  </a>
           <a role="button" class="btn btn-primary" href="/vm?action=stop&vmid=${m.get('vmid')}&node=${m.get('node')}&type=${m.get('type')}">
     	   <span class="glyphicon glyphicon-stop"></span>
      	   ${loc.translate(_("Stop"))}
   	   </a>

	  % endif
               <a role="button" class="btn btn-primary disabled" href="/vm?action=reboot&vmid=${m.get('vmid')}&node=${m.get('node')}&type=${m.get('type')}">
	       <span class="glyphicon glyphicon-eject"></span>
	       ${loc.translate(_("Reboot"))}
	       </a>

  <a data-toggle="modal" href="#modalSettings" class="btn btn-primary">${loc.translate(_("Settings"))}</a>

  <div class="modal fade" id="modalSettings" tabindex="-1" role="dialog" aria-labelledby="modalSettingsLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
          <h4 class="modal-title">${loc.translate(_("Settings"))}</h4>
        </div>
        <div class="modal-body">
          ${m}
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-default" data-dismiss="modal">${loc.translate(_("Close"))}</button>
        </div>
      </div>
    </div>
  </div>

   % endfor

%else:
 % if not errmessage:
 <div class='bs-callout bs-callout-danger'>
      <h4>${loc.translate(_("Nothing found"))}</h4>
      <p>${loc.translate(_("No virtual machines found for your account"))}</p>
 </div>
 %else:
   <div class='bs-callout bs-callout-danger'>
      <h4>${loc.translate(_("Connection error"))}</h4>
      <p>${errmessage}</p>
 </div>
 %endif
%endif
<br>
