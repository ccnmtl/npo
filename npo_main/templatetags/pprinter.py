from django import template
from django.template.defaultfilters import stringfilter
from pprint import pformat
from django.utils.simplejson import loads

register = template.Library()

@register.filter
def pprint(obj):
    return pformat(obj)

@register.filter
def pprint_json(string):
    try:
        return pformat(loads(string))
    except ValueError:
        return string
