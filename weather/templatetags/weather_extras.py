from django import template

register = template.Library()


@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter. Usage: "a,b,c"|split:"," """
    return value.split(delimiter)