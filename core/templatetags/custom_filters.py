from django import template
import locale

register = template.Library()

@register.filter(name='currency')
def currency(value):
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'C')

    try:
        value = float(value)
    except (ValueError, TypeError):
        return value  # Devuelve el valor sin formatear si no se puede convertir a float

    return locale.format_string("%0.2f", value, grouping=True)

@register.filter(name='add_class')
def add_class(value, arg):
    css_classes = value.field.widget.attrs.get('class', '')
    if css_classes:
        css_classes += f' {arg}'
    else:
        css_classes = arg
    value.field.widget.attrs['class'] = css_classes
    return value

@register.filter(name='add_attr')
def add_attr(value, arg):
    key, val = arg.split(":")
    value.field.widget.attrs[key] = val
    return value

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)
