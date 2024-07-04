from django import template

register = template.Library()

@register.filter
def multiply_and_round(value):
    multiplied_value = value * 1.4
    rounded_value = round(multiplied_value / 5) * 5
    return rounded_value