var plot = function(insertInto, paramsFrom) {
  var div = document.getElementById(insertInto);

  var table = document.getElementById(paramsFrom);

  div.innerHTML = "";

  var xs = MochiKit.Selector.findChildElements(table, ["td:first-child input"]);
  var ys = MochiKit.Selector.findChildElements(table, ["td:last-child input"]);

  var params = "";
  for( x=0; x<xs.length; ++x ) {
    params += "x=" + xs[x].value + "&";
  }
  for( y=0; y<ys.length; ++y ) {
    params += "y=" + ys[y].value + "&";
  }

  var img = MochiKit.DOM.IMG({"src": "http://hotdog.ccnmtl.columbia.edu/curve?" + params + "dpi=40",
                              "width": div.style.width, "height": div.style.height
            });

  var link = MochiKit.DOM.A({"href": "http://hotdog.ccnmtl.columbia.edu/curve?" + params + "dpi=100",
                             "target": "_blank"
            });

  MochiKit.DOM.appendChildNodes(link, img);
  MochiKit.DOM.appendChildNodes(div, link);

  return false;
};
