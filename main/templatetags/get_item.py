# main/templatetags/get_item.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key), 'No Answer')
