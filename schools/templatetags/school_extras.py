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


@register.filter
def facility_icon(facility_name):
    """Map facility name to Material Icon"""
    icon_map = {
        'AC': 'ac_unit',
        'Canteen': 'restaurant',
        'Library': 'menu_book',
        'Sports Complex': 'sports_soccer',
        'Computer Lab': 'computer',
        'Science Lab': 'science',
        'Swimming Pool': 'pool',
        'Auditorium': 'theater_comedy',
    }
    # Case-insensitive lookup
    for key, icon in icon_map.items():
        if key.lower() in facility_name.lower():
            return icon
    return 'check_circle'  # Default icon

