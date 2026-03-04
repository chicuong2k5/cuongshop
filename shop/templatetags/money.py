from django import template

register = template.Library()

@register.filter
def vnd(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except:
        return value

@register.filter
def mul(value, arg):
    try:
        return value * arg
    except:
        return 0