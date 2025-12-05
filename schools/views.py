from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg, Count
from django_filters import FilterSet, CharFilter, ChoiceFilter, BooleanFilter, NumberFilter
from .models import School, Facility, Review


class SchoolFilter(FilterSet):
    """Filter for school search"""
    name = CharFilter(field_name='name', lookup_expr='icontains', label='School Name')
    board = ChoiceFilter(choices=School.BOARD_CHOICES)
    grade = CharFilter(method='filter_by_grade', label='Grade')
    co_ed_type = ChoiceFilter(choices=School.CO_ED_CHOICES)
    pin_code = CharFilter(field_name='pin_code', lookup_expr='exact')
    distance_max = NumberFilter(field_name='distance', lookup_expr='lte', label='Max Distance (km)')
    bus_availability = BooleanFilter(field_name='bus_availability')
    facilities = CharFilter(method='filter_by_facilities')
    min_rating = NumberFilter(field_name='rating', lookup_expr='gte', label='Min Rating')
    
    class Meta:
        model = School
        fields = ['name', 'board', 'grade', 'co_ed_type', 'pin_code', 'distance_max', 'bus_availability', 'min_rating']
    
    def filter_by_grade(self, queryset, name, value):
        """Filter schools that offer the specified grade"""
        if value:
            return queryset.filter(grades_offered__icontains=value)
        return queryset
    
    def filter_by_facilities(self, queryset, name, value):
        """Filter schools by facilities (comma-separated facility IDs)"""
        if value:
            facility_ids = [int(fid) for fid in value.split(',') if fid.isdigit()]
            if facility_ids:
                return queryset.filter(facilities__id__in=facility_ids).distinct()
        return queryset


def home_view(request):
    """Home page with recommended schools"""
    recommended_schools = School.objects.all().order_by('-rating')[:6]
    context = {
        'recommended_schools': recommended_schools,
    }
    return render(request, 'home.html', context)


def school_search_view(request):
    """School search and filter page"""
    schools = School.objects.all().annotate(
        review_count=Count('reviews')
    )
    
    # Apply filters
    school_filter = SchoolFilter(request.GET, queryset=schools)
    schools = school_filter.qs
    
    # Get sorting parameter
    sort_by = request.GET.get('sort', 'rating')
    if sort_by == 'distance':
        schools = schools.order_by('distance')
    elif sort_by == 'fees':
        schools = schools.order_by('fees_by_grade')
    else:
        schools = schools.order_by('-rating', 'name')
    
    # Get all facilities for filter options
    all_facilities = Facility.objects.all()
    
    # Get selected filters for display
    selected_facilities = request.GET.getlist('facilities')
    selected_grade = request.GET.get('grade', '')
    
    context = {
        'schools': schools,
        'filter': school_filter,
        'all_facilities': all_facilities,
        'selected_facilities': selected_facilities,
        'selected_grade': selected_grade,
        'board_choices': School.BOARD_CHOICES,
        'co_ed_choices': School.CO_ED_CHOICES,
    }
    return render(request, 'search.html', context)


def school_detail_view(request, school_id):
    """School detail page"""
    school = get_object_or_404(School, pk=school_id)
    reviews = Review.objects.filter(school=school).order_by('-created_at')
    
    # Calculate rating distribution
    rating_dist = {}
    total_reviews = reviews.count()
    for i in range(1, 6):
        rating_dist[i] = reviews.filter(rating=i).count()
    
    # Convert to list of tuples for easier template iteration
    rating_dist_list = [(i, rating_dist[i], rating_dist[i] / total_reviews * 100 if total_reviews > 0 else 0) 
                        for i in range(5, 0, -1)]
    
    # Get average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'school': school,
        'reviews': reviews[:10],  # Show first 10 reviews
        'rating_distribution': rating_dist,
        'rating_distribution_list': rating_dist_list,
        'total_reviews': total_reviews,
        'average_rating': round(avg_rating, 1) if avg_rating else school.rating,
    }
    return render(request, 'school_detail.html', context)
