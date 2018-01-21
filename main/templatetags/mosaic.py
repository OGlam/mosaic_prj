from django import template
from django.forms import CheckboxInput, FileInput, RadioSelect, CheckboxSelectMultiple, SelectMultiple, Select
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


@register.filter(name='is_file')
def is_file(field):
    return field.field.widget.__class__.__name__ == FileInput().__class__.__name__


@register.filter(name='is_radio')
def is_radio(field):
    return field.field.widget.__class__.__name__ == RadioSelect().__class__.__name__


@register.filter(name='is_checkbox_multi')
def is_checkbox_multi(field):
    return field.field.widget.__class__.__name__ == CheckboxSelectMultiple().__class__.__name__


@register.filter(name='is_select_multi')
def is_select_multi(field):
    return field.field.widget.__class__.__name__ == SelectMultiple().__class__.__name__


@register.filter(name='is_select')
def is_select(field):
    return field.field.widget.__class__.__name__ == Select().__class__.__name__


@register.filter
def boolean_to_icon(arg):
    if arg:
        return mark_safe('<span class="fa fa-check green-icon"></span>')
    else:
        return mark_safe('<span class="fa fa-times red-icon"></span>')


@register.simple_tag
def svg_icon(icon_name, class_name='', simple=False, from_upload=False, rtl=False):
    if icon_name is None:
        return ''
    result = '<span class="svg-icon {}">'.format(class_name)
    if from_upload:
        file = open(icon_name, 'r')
        result += file.read()
        file.close()
    elif simple:
        result += render_to_string('svgs/{}.svg'.format(icon_name))
    else:
        result += render_to_string('svgs/{}{}.svg'.format(icon_name, '_he' if rtl else '_en'))
    result += '</span>'
    return mark_safe(result)


@register.simple_tag
def bidi(instance, field):
    lang = translation.get_language()[:2]
    return getattr(instance, field + "_" + lang)


@register.filter
def bd(instance, field):
    lang = translation.get_language()[:2]
    return getattr(instance, field + "_" + lang)


@register.filter
def bd_first_letter(instance, field):
    lang = translation.get_language()[:2]
    res = getattr(instance, field + "_" + lang).upper()
    first_letter = res[0] if res else ''
    match = re.match('[a-mA-M]', first_letter)
    if match:
        return 'A-M'
    else:
        return 'N-Z'


def bd_first_letter_am(instance, field):
    lang = translation.get_language()[:2]
    res = getattr(instance, field + "_" + lang).upper()
    first_letter = res[0] if res else ''
    match = re.match('[a-mA-M]', first_letter)
    if match:
        return True
    else:
        return False

