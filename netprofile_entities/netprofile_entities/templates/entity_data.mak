<tpl if="data.house || data.address">
	<img class="np-inline-img" src="/static/entities/img/house_small.png" />
	{data.address} {data.house} {data.entrance} {data.floor} {data.flat}
</tpl>
<tpl if="data.phone_home || data.phone_work || data.phone_cell || data.cp_phone_work || data.cp_phone_cell">
<tpl if="data.house || data.address"><br /></tpl>
<tpl if="data.phone_home">
	<img class="np-inline-img" src="/static/entities/img/phone_small.png" />
	{data.phone_home}
</tpl>
<tpl if="data.phone_work">
	<img class="np-inline-img" src="/static/entities/img/phone_small.png" />
	{data.phone_work}
</tpl>
<tpl if="data.phone_cell">
	<img class="np-inline-img" src="/static/entities/img/mobile_small.png" />
	{data.phone_cell}
</tpl>
<tpl if="data.cp_phone_work">
	<img class="np-inline-img" src="/static/entities/img/phone_small.png" />
	{data.cp_phone_work}
</tpl>
<tpl if="data.cp_phone_cell">
	<img class="np-inline-img" src="/static/entities/img/mobile_small.png" />
	{data.cp_phone_cell}
</tpl>
</tpl>

