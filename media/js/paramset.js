
function clearText(field){
    if (field.defaultValue == field.value) field.value = '';
    else if (field.value == '') field.value = field.defaultValue;
}


function hideAllParamSet() {
	//Loop through the seclect menu values and hide all
	var selectParamSet = document.getElementById("selectParamSet");
  if(selectParamSet) {
	for (var i=0; i<=selectParamSet.options.length -1; i++) {
		hideElement(selectParamSet.options[i].value);
	}

  }
}

function toggleParam(showID) {
	if (showID != "") {
		hideAllParamSet(); // Hide all
		showElement(showID); // Show the one we asked for
	}

}

function select_all (s) {
    for (i=0; i<s.length; i++)
        s.options[i].selected = 1;
}

function selectAllMulties() {
  var multiselects = getElementsByTagAndClassName("select","form_multiselect");
  for (var i=0; i<multiselects.length; i++) {
    select_all(multiselects[i]);
  }
}

function insensitiveSort(a,b) {
  string = a + b
  a = a.toLowerCase()
  b = b.toLowerCase()
  if (a < b) return -1;
  if (a > b) return 1;
  return 0;
}

function numOrdA(a, b){ return (a-b); }
function numOrdD(a, b){ return (b-a); }

function AddListItem(id) {
  var from = $("input-" + id);
  var to = $("select-" + id);

  var tbox = new Array();

  for (var i=0; i<to.length; i++) {
    if (to.options[i].value == -1) continue;
    tbox[i] = to.options[i].text;
  }
  tbox.push(from.value);
  tbox.sort(numOrdA);

  for (i=0; i<tbox.length; i++)
    to[i] = new Option(tbox[i], tbox[i]);
  from.value = "";
}

function RemoveListItems(id) {
  var from = $("select-" + id);
  var newarr = new Array();

  var j=0;
  for (var i=0; i<from.length; i++) {
    if (from.options[i].selected) continue;
    newarr[j++] = from.options[i].text;
  }

  from.length = 0;
  for (i=0; i<newarr.length; i++) {
    from[i] = new Option(newarr[i],newarr[i]);
  }
}

addLoadEvent(hideAllParamSet)
