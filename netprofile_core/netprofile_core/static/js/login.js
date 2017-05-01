var fld;

fld = document.getElementById('user');
if(fld)
{
	fld.value = '';
	fld.focus();
}

fld = document.getElementById('pass');
if(fld)
	fld.value = '';

function on_change_lang()
{
	var f, q, re;

	f = document.getElementById('user');
	if(f.value === '')
	{
		f = document.getElementById('__locale');
		if(f)
		{
			q = window.location.search;
			if(q)
			{
				re = /__locale=[\w_-]+/;
				if(q.match(re))
					q = q.replace(re, '__locale=' + f.value);
				else
					q += '&__locale=' + f.value;
			}
			else
				q = '?__locale=' + f.value;
			window.location.search = q;
		}
	}
	return false;
}

fld = document.getElementById('__locale');
if(fld)
	fld.onchange = on_change_lang;

