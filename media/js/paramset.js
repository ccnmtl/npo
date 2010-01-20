
function clearText(field){
    if (field.defaultValue == field.value) field.value = '';
    else if (field.value == '') field.value = field.defaultValue;
}


function hideAllParamSet() {
	//Loop through the seclect menu values and hide all
	var selectParamSet = document.getElementById("selectParamSet");
	for (var i=0; i<=selectParamSet.options.length -1; i++) {
		hideElement(selectParamSet.options[i].value);
	}
}

function toggleParam(showID) {
	if (showID != "") {
		hideAllParamSet(); // Hide all
		showElement(showID); // Show the one we asked for
	}

}

addLoadEvent(hideAllParamSet)
