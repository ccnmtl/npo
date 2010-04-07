var styleHistogramForms = function() {
  var forms = getElementsByTagAndClassName("form","histogram_params");
  for( var i=0; i<forms.length; ++i ) {
    styleForm(forms[i]);
  };
};

var spanText = function(val) {
  return val + " &mdash; ";
};

var validateForm = function(form) {
  var paramEls = MochiKit.Selector.findChildElements(form, ["input.param"]);
  for( var i=0; i<paramEls.length; ++i ) {
    var paramEl = paramEls[i];
    var floorVal = 0;
    if( i>0 ) floorVal = paramEls[i-1].value;
    var myVal = parseFloat(paramEl.value);
    floorVal = parseFloat(floorVal);
    if( myVal <= floorVal ) {
      return false;
    };
  };
  return true;
};

var validateAndRestyleForm = function(form) {
  if( !validateForm(form) ) {
    alert("Bins must not overlap. Please correct the error before continuing.");
    var submit = MochiKit.Selector.findChildElements(form, ["input[type=submit]"]);
    submit[0].disabled = "true";
    return false;
  };
  var submit = MochiKit.Selector.findChildElements(form, ["input[type=submit]"]);
  submit[0].disabled = false;
  styleForm(form);
};

var styleForm = function(form) {
  var spanEls = MochiKit.Selector.findChildElements(form, ["span.paramCue"]);
  for( var i=0; i<spanEls.length; ++i ) {
    MochiKit.DOM.removeElement(spanEls[i]);
  };
  var paramEls = MochiKit.Selector.findChildElements(form, ["input.param"]);
  for( var i=0; i<paramEls.length; ++i ) {
    var paramEl = paramEls[i];
    var floorVal = 0;
    if( i>0 ) floorVal = paramEls[i-1].value;
    var span = MochiKit.DOM.SPAN({"class": "paramCue"});
    span.innerHTML = spanText(floorVal);
    MochiKit.DOM.insertSiblingNodesBefore(paramEl, span);
  };

  var span = MochiKit.Selector.findChildElements(form, ["span.finalParamCue"])[0];
  span.innerHTML = paramEls[paramEls.length-1].value + " and greater";
};

var addInterval = function(form, name, floor, ceiling) {
  var paramEls = MochiKit.Selector.findChildElements(form, ["input.param"]);

  /* First do validation -- make sure the new interval
   * isn't going to span more than one existing bin.
   */
  for( var i=0; i<paramEls.length; ++i ) {
    var paramEl = paramEls[i];
    var myFloorVal = 0;
    if( i>0 ) myFloorVal = paramEls[i-1].value;
    var myCeilingVal = parseFloat(paramEl.value);
    myFloorVal = parseFloat(myFloorVal);
    if( floor<=myFloorVal && ceiling>=myCeilingVal ) {
      alert("You are trying to add a new bin that spans more than one existing bin. You can't do that.");
      return false;
    };
  };

  /* If both ends of the new interval are greater than
   * all the intervals we currently have, we need to add
   * two new bins, not just one.
   */
  var myFloorVal = parseFloat(paramEls[paramEls.length-1].value);
  if( floor > myFloorVal && ceiling > myFloorVal ) {
    addInterval(form, name, myFloorVal, floor);

    // We need to re-get the params since the list has grown during the recursive call
    paramEls = MochiKit.Selector.findChildElements(form, ["input.param"]);
  };

  var newInput = MochiKit.DOM.INPUT({"class": "param",
				     "type": "text",
				     "name": name,
				     "onchange": "validateAndRestyleForm(this.parentNode.parentNode)"});
  var newInputDiv = MochiKit.DOM.DIV();
  MochiKit.DOM.appendChildNodes(newInputDiv, newInput);

  /* OK, the new interval validated alright.
   * Now we'll figure out where to put it.
   */
  for( var i=0; i<paramEls.length; ++i ) {
    var paramEl = paramEls[i];
    var myFloorVal = 0;
    if( i>0 ) myFloorVal = paramEls[i-1].value;
    var myCeilingVal = parseFloat(paramEl.value);
    myFloorVal = parseFloat(myFloorVal);

    if( floor <= myCeilingVal ) {
      newInput.value = ceiling;
      MochiKit.DOM.insertSiblingNodesAfter(paramEl.parentNode,
					    newInputDiv);
      paramEl.value = floor;
      validateAndRestyleForm(form);
      return 1;
    };
  };
  var paramEl = paramEls[paramEls.length-1];
  newInput.value = ceiling;
  MochiKit.DOM.insertSiblingNodesAfter(paramEl.parentNode,
				       newInputDiv);
  paramEl.value = floor;
  validateAndRestyleForm(form);
  return 1;
};

var newFormInterval = function(div, form, name) {
  var inputs = MochiKit.Selector.findChildElements(
		 div, ["input.newbin"]);
  var a = inputs[0].value;
  var b = inputs[1].value;
  var floor = a < b && a || b;
  var ceiling = floor == a && b || a;
  addInterval(form, name, floor, ceiling);

};