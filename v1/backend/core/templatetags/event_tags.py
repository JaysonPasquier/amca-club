from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def add_hours(value, hours):
    """Add a specified number of hours to a datetime."""
    if not value:
        return value
    try:
        dt = datetime.strptime(value, '%Y%m%dT%H%M%S')
        dt = dt + timedelta(hours=int(hours))
        return dt.strftime('%Y%m%dT%H%M%S')
    except:
        return value
