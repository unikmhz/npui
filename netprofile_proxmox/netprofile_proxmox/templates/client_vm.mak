## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>
% if message:
<div class='bs-callout bs-callout-info'>
<h4>Action complete</h4>
<p>You have ${message}ed your VM</p>
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
      	   Start
   	  </a>
           <a role="button" class="btn btn-primary disabled" href="/vm?action=stop&vmid=${m.get('vmid')}&node=${m.get('node')}&type=${m.get('type')}">
     	   <span class="glyphicon glyphicon-stop"></span>
      	   Stop
   	   </a>

     	 % else:
	    <a role="button" class="btn btn-success active">
	    <span class="glyphicon glyphicon-fishes"></span>
	    ${m.get('name')}
	    </a>

           <a role="button" class="btn btn-primary disabled" href="/vm?action=start&vmid=${m.get('vmid')}&node=${m.get('node')}&type=${m.get('node')}">
      	   <span class="glyphicon glyphicon-play"></span>
      	   Start
   	  </a>
           <a role="button" class="btn btn-primary" href="/vm?action=stop&vmid=${m.get('vmid')}&node=${m.get('node')}&type=${m.get('type')}">
     	   <span class="glyphicon glyphicon-stop"></span>
      	   Stop
   	   </a>

	  % endif
               <a role="button" class="btn btn-primary disabled" href="/vm?action=reboot&vmid=${m.get('vmid')}&node=${m.get('node')}&type=${m.get('type')}">
	       <span class="glyphicon glyphicon-eject"></span>
	       Reboot
	       </a>

  <a data-toggle="modal" href="#modalSettings" class="btn btn-primary">Settings</a>

  <div class="modal fade" id="modalSettings" tabindex="-1" role="dialog" aria-labelledby="modalSettingsLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
          <h4 class="modal-title">Settings</h4>
        </div>
        <div class="modal-body">
          ${m}
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>

   % endfor

%else:
 % if not errmessage:
 <div class='bs-callout bs-callout-danger'>
      <h4>Nothing found</h4>
      <p>No virtual machines found for your account</p>
 </div>
 %else:
   <div class='bs-callout bs-callout-danger'>
      <h4>Connection error</h4>
      <p>${errmessage}</p>
 </div>
 %endif
%endif
<br>
