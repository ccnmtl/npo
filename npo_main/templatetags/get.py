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

@register.filter
def get_tuples(dict,key):
  """the params dictionary stores demand curve parameters as something like:

500 0.2
1000 0.59
5000 1.53
10000 2.5

we need to return it as a list of tuples so the template can iterate over it """
  try:
    return [l.split(" ") for l in dict.get(key,"").split("\n")]
  except:
    return []
