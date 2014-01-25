## -*- coding: utf-8 -*-
			<form class="row" role="form" method="post" action="${req.route_url('stashes.cl.accounts', traverse=(stash.id, 'chrate'))}">
				<label for="fld-chrate-${a.id}" class="col-sm-4">${_('New Next Rate')}</label>
				<div class="col-sm-8 form-inline">
					<input type="hidden" name="csrf" value="${req.get_csrf()}" />
					<input type="hidden" name="entityid" value="${a.id}" />
					<select class="form-control chosen-select padded-wrap" id="fld-chrate-${a.id}" name="rateid" title="${_('Next Rate')}">
% for rate in rates:
						<option label="${rate}" value="${rate.id}"\
% if (a.next_rate_id and (rate.id == a.next_rate_id)) or ((not a.next_rate_id) and (rate.id == a.rate_id)):
 selected="selected"\
% endif
>${rate}</option>
% endfor
					</select>
					<span class="btn-group">
						<button class="btn btn-default" type="submit" name="submit" title="${_('Select different next rate')}">${_('Set')}</button>
% if a.next_rate_id:
						<button class="btn btn-default" type="submit" name="clear" title="${_('Cancel scheduled rate change')}">${_('Clear')}</button>
% endif
					</span>
				</div>
			</form>

