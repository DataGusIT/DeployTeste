from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acessar itens de dicionário no template usando chave dinâmica"""
    return dictionary.get(key)