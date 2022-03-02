from django import template

register = template.Library()

@register.filter
def get_type(value):
    print('hhhhhhhhhhhhhhhhhhhhhhh',value)
    return type(value)

@register.filter(name='times') 
def times(number):
    return range(number)