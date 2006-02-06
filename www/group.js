function removeSelected(element)
{
	var selectedOptions = new Array();

	var count = 0;
	for (var i=element.options.length-1; i>=0; i--)
	{
		if (element.options[i].selected)
		{
			selectedOptions[count++] = element.options[i].text;
			element.remove(i);
		}
	}

	return selectedOptions;
}

function add(element, options)
{
	for (var i=0; i<options.length; i++)
	{
		var optn = document.createElement('option');
		optn.text = options[i];
		optn.value = options[i];
		element.options.add(optn);
	}
}

function moveout(form)
{
	selected = removeSelected(form.ingroup);
	add(form.outgroup, selected);
}

function movein(form)
{
	selected = removeSelected(form.outgroup);
	add(form.ingroup, selected);
}

function selectAllIn(form)
{
	for (var i=0; i<form.ingroup.options.length; i++)
	{
		form.ingroup.options[i].selected = 1;
	}
}
