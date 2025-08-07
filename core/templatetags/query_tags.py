# em core/templatetags/query_tags.py

from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Pega a query string da URL atual e permite adicionar/alterar parâmetros.
    Uso no template: {% query_transform page=2 %}
    """
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()

# ================================================================= #
# ADICIONE ESTA NOVA TAG PARA RESOLVER O ERRO DE SINTAXE            #
# ================================================================= #
@register.simple_tag(takes_context=True)
def build_query(context, key, value):
    """
    Constrói uma query string mantendo os parâmetros existentes.
    Alternativa mais segura para o **{key: value}.
    """
    query = context['request'].GET.copy()
    query[key] = value
    return query.urlencode()