/* The problem: linking to an element in a non-active
 * tabber tab fails, because the tab's hidden contents
 * are not findable.
 *
 * So, this function will activate the appropriate
 * tabber tab.
 *
 * @param el: an <a> tag whose href is a fragment
 * on the same page, which is inside a tabber tab.
 *
 * (It's intended to be used as the onclick handler
 * for those anchors.)
 *****/
function expandTab(el) {
  var href = el.hash.substr(1);
  var to = getElement(href);
  if( !MochiKit.DOM.hasElementClass(
        to.parentNode, "tabbertab") )
    return 1;
  var key = to.innerHTML;
  var tabButton = MochiKit.Selector.findChildElements(to.parentNode.parentNode,
                    ["ul.tabbernav li a#" + key])[0];
  tabButton.onclick();
  return 1;
};
