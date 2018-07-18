from django import template
from CryptoHashCode import *

register = template.Library()


@register.assignment_tag
def get_hash_value(val):
    return toHashVal(val)




