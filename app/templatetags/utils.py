from django import template

register = template.Library()

@register.filter
def get_type(value):
    print('hhhhhhhhhhhhhhhhhhhhhhh',value)
    return type(value)

@register.filter(name='times') 
def times(number):
    return range(number)

from django.conf import settings

@register.filter
def adjust_for_pagination(value, page):
    value, page = int(value), int(page)
    adjusted_value = value + ((page - 1) * settings.RESULTS_PER_PAGE)
    return adjusted_value