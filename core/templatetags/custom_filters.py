from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    """Agrega una clase CSS a un campo de formulario."""
    css_classes = value.field.widget.attrs.get('class', '')
    if css_classes:
        css_classes += f' {arg}'
    else:
        css_classes = arg
    value.field.widget.attrs['class'] = css_classes
    return value


@register.filter(name='add_attr')
def add_attr(value, arg):
    """Agrega un atributo adicional a un campo de formulario."""
    key, val = arg.split(":")
    value.field.widget.attrs[key] = val
    return value