## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>
<script type='text/javascript'>
function createWallet(wallet, url, resultid) {
        jQuery.ajax({
            url:     url,
            type:     "GET",
            dataType: "JSON",
	    data: ({newwallet: wallet}),
            error: function (){
                alert("${loc.translate(_("Connection error"))}");
            },
    	      beforeSend: function () {
	      document.getElementById(resultid).innerHTML = "${loc.translate(_("Creating new wallet..."))}";
	      },
            success: function(response){
                document.getElementById(resultid).innerHTML = "${loc.translate(_("New wallet created"))}";
		location.reload();
             }
        });
   }
</script>

<script type='text/javascript'>
function exportPrivKey(addrid, url, resultid) {
        jQuery.ajax({
            url:     url,
            type:     "GET",
            dataType: "JSON",
	    data: ({addr: addrid}),
            error: function (){
                alert("${loc.translate(_("Connection error"))}");
            },
            success: function(response){
                document.getElementById(resultid).innerHTML = response['privkey'];
             }
        });
   }
</script>

<script type="text/javascript">
function importKey(result_id, form_id, url) {
        jQuery.ajax({
              url:     url,
              type:     "POST",
              dataType: "JSON",
              data: jQuery("#"+form_id).serialize(), 
	      beforeSend: function () {
	      document.getElementById(result_id).innerHTML = "${loc.translate(_("Creating new wallet..."))}";
	      },
              success: function(response) {
              document.getElementById(result_id).innerHTML = response['pubkey'];
              },
              error: function(response) { 
             document.getElementById(result_id).innerHTML = "${loc.translate(_("Server connection error"))}";
              }
            });
        }
</script>

% if message:
  <div class='bs-callout bs-callout-info'>
       <h4>${loc.translate(_("Ready"))}</h4>
       <p>${loc.translate(_("Action successfully completed"))}</p>
  </div>
% endif

% if len(wallets) == 0:
  <div class="alert alert-warning">
  ${loc.translate(_("You have no wallets yet."))} 
  </div>
% else:
  % for w in wallets:
  <div class="alert alert-info">
    ${loc.translate(_("Balance for wallet"))} <strong>${w['wallet']}</strong>
    % for addr in w['address']:
      [${addr}] <a data-toggle='modal' href='#modalExport${addr}' onClick="exportPrivKey('${addr}','${request.route_url("bitcoin.cl.export")}', 'resp${addr}');">${loc.translate(_("Export Private Key"))}</a>
   <div class="modal fade" id="modalExport${addr}" tabindex="-1" role="dialog" aria-labelledby="modalExportLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
          <h4 class="modal-title">${loc.translate(_("Private Key Export"))}</h4>
        </div>
        <div class="modal-body" id="resp${addr}">
	${loc.translate(_("Wait please..."))}
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-default" data-dismiss="modal">${loc.translate(_("Close"))}</button>
        </div>
      </div>
    </div>
  </div>

    % endfor  
    ${loc.translate(_("is"))} ${w['balance']} ${loc.translate(_("BTC"))}
  </div> 
  % endfor

  <a data-toggle='modal' href='#modalImport' class="btn btn-primary" >${loc.translate(_("Import Private Key"))}</a>

   <div class="modal fade" id="modalImport" tabindex="-1" role="dialog" aria-labelledby="modalImportLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
          <h4 class="modal-title">${loc.translate(_("Private Key Import"))}</h4>
        </div>
        <div class="modal-body" id="importDiv">
	## тут POST
	<form id="importForm" class="form-inline" role="form" action="" method='POST'>
	<div class="form-group">
	    <label class="sr-only" for="PrivateKey">Private Key</label>
	    <input type="text" class="form-control" name="privkey" placeholder=${loc.translate(_("Enter Private Key"))}>
	    <input type="hidden" name="nextwallet" value="${nextwallet}">
	    <button type="submit" class="btn btn-default" onclick="importKey('importDiv', 'importForm', '${request.route_url("bitcoin.cl.create")}')">${loc.translate(_("Import"))}</button>
	
	</form>
  </div>

        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-default" data-dismiss="modal">${loc.translate(_("Close"))}</button>
        </div>
      </div>
    </div>
  </div>

% endif
<a role="button" onclick="createWallet('${nextwallet}', '${request.route_url("bitcoin.cl.create")}', 'newWallet')" class="btn btn-warning active"><div id="newWallet">${loc.translate(_("Create a new wallet"))}</div></a>
  
<%doc>
if wallets are empty, show 2 buttons, add new and import priv.key
else show same and export priv.key
import and export keys should be inserted in the bootstrap modal dialogs
after adding and importing user should be redirected to main wallet page
importing can take some time so imported key cannot be visible at once. it should be showed a loading indicator. 
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
</%doc>
<br>
