from django import template
register = template.Library()

@register.filter
def get( dict, key, default = '' ):
  """
  Usage: 

  view: 
  some_dict = {'keyA':'valueA','keyB':{'subKeyA':'subValueA','subKeyB':'subKeyB'},'keyC':'valueC'}
  keys = ['keyA','keyC']
  template: 
  {{ some_dict|get:"keyA" }}
  {{ some_dict|get:"keyB"|get:"subKeyA" }}
  {% for key in keys %}{{ some_dict|get:key }}{% endfor %}
  """

  try:
    return dict.get(key,default)
  except:
    return default

@register.filter
def getlist(dict, key, default = None):
    """ this is for simple list parameters (like "available engine sizes").
    fetches the parameters and splits it on whitespace, returning a list
    """
    if default is None:
        default = ""
    try:
        return dict.get(key,default).split(" ")
    except:
        return []
