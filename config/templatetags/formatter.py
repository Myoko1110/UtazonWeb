from typing import Union

from django import template
register = template.Library()


@register.filter
def format_price(price):
    return f"{price:,.2f}"


@register.filter
def format_review(average: Union[float, int]):
    return f"{average:.1f}"


@register.filter
def digit_grouping(number: Union[float, int]):
    return f"{number:,}"
