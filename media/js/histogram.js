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
    myVal = parseFloat(paramEl.value);
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
