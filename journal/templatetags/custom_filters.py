from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    if dictionary is None:
        return []
    return dictionary.get(key, [])

@register.filter
def flatten(value):
    """Flatten a list of lists into a single list."""
    result = []
    if value:
        for item in value:
            if isinstance(item, (list, tuple)):
                result.extend(item)
            else:
                result.append(item)
    return result
