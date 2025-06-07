from django import template

register = template.Library()

@register.filter
def getattr(obj, attr):
    """Template filter to get attribute value from object"""
    try:
        return getattr(obj, attr)
    except AttributeError:
        return None
