from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Adiciona classes CSS a um campo de formulário do Django
    """
    return value.as_widget(attrs={'class': arg})
