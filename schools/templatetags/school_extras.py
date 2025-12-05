from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary is None:
        return None
    return dictionary.get(key, 0)


@register.filter
def get_fee(school, grade):
    """Get fee for a specific grade"""
    try:
        grade_int = int(grade)
        return school.get_fee_for_grade(grade_int)
    except (ValueError, AttributeError):
        return None

