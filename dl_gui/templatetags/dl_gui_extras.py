from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def url_attr(context, label, attribute):
    request = context["request"]
    if request.path.lower().startswith(reverse(label)):
        return attribute
    return ""
