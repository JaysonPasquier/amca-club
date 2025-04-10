from django import template
from django.utils.safestring import mark_safe

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

@register.filter(name='attr')
def set_attr(field, attr_string):
    """
    Ajoute des attributs à un champ de formulaire
    Syntaxe: {{ field|attr:"name:value" }}
    """
    # Check if we're dealing with a form field or a SafeString (from previous filter)
    if hasattr(field, 'as_widget'):
        # This is a form field
        attrs = {}
        pairs = attr_string.split('|')
        for pair in pairs:
            key, value = pair.split(':', 1)
            attrs[key] = value
        return field.as_widget(attrs=attrs)
    else:
        # This is likely a SafeString from a previous filter application
        # Try to add the attribute directly to the HTML
        attr_name, attr_value = attr_string.split(':', 1)
        html = str(field)
        # If this is a input/textarea/select, add attribute before closing bracket
        if '<input' in html or '<textarea' in html or '<select' in html:
            # Find position of first closing bracket
            pos = html.find('>')
            if pos > 0:
                html = html[:pos] + f' {attr_name}="{attr_value}"' + html[pos:]

        return mark_safe(html)
