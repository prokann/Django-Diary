from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def unpack(value):
    val = [i for i in value]
    return val[0]


@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)


@register.filter(name='range')
def filter_range(start, end):
    return range(start, end)


@register.simple_tag
def checkbox_input(need, done='', id=''):
    if id:
        if done:
            return mark_safe(f'<input type="checkbox" id="{need}" name="days[]" value="{id}" checked>')
        else:
            return mark_safe(f'<input type="checkbox" id="{need}" name="days[]" value="{id}">')

    else:
        if done:
            return mark_safe(f'<input type="checkbox" id="{need}" name="days[]" value="{need}" checked>')
        else:
            return mark_safe(f'<input type="checkbox" id="{need}" name="days[]" value="{need}">')

