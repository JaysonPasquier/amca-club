from django import template
register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg

@register.filter(name='get_range')
def get_range(value):
    """
    Filtre pour générer une liste de nombres de 0 à value-1
    Usage: {% for i in 5|get_range %} donnera [0, 1, 2, 3, 4]
    """
    return range(int(value))
