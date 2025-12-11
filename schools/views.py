from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg, Count
from django_filters import FilterSet, CharFilter, ChoiceFilter, BooleanFilter, NumberFilter
from .models import School, Facility, Review
from curriculum.models import Curriculum
from .utils import calculate_distance


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
    """Home page with recommended schools and curricula"""
    recommended_schools = School.objects.select_related().prefetch_related('facilities').order_by('-rating')[:10]
    curricula = Curriculum.objects.all()[:10]
    
    # Pre-calculate fees for each school to avoid repeated method calls
    for school in recommended_schools:
        school.default_fee = school.get_default_fee()
    
    context = {
        'recommended_schools': recommended_schools,
        'curricula': curricula,
    }
    return render(request, 'home.html', context)




def school_search_view(request):
    """School search form page (Uber-style)"""
    # Get selected values from query params for form state (if user comes back to form)
    selected_boards = request.GET.getlist('board', [])
    selected_ratings = request.GET.getlist('rating', [])
    selected_bus = request.GET.getlist('bus', [])
    selected_co_ed = request.GET.getlist('co_ed_type', [])
    distance_max = request.GET.get('distance_max', '50')
    
    context = {
        'board_choices': School.BOARD_CHOICES,
        'selected_boards': selected_boards,
        'selected_ratings': selected_ratings,
        'selected_bus': selected_bus,
        'selected_co_ed': selected_co_ed,
        'distance_max': distance_max,
    }
    return render(request, 'search_form.html', context)


def school_search_results_view(request):
    """School search results page"""
    schools = School.objects.prefetch_related('facilities')
    
    # Get search parameters
    name = request.GET.get('name', '')
    boards = request.GET.getlist('board')  # Multiple boards
    grade = request.GET.get('grade', '')
    user_pin_code = request.GET.get('user_pin_code', '').strip()
    distance_max = request.GET.get('distance_max', '50')  # Distance slider max value
    ratings = request.GET.getlist('rating')  # Multiple ratings (1-5)
    bus_availability = request.GET.getlist('bus')  # Multiple bus options
    co_ed_types = request.GET.getlist('co_ed_type')  # Multiple co-ed types
    
    # Apply filters
    if name:
        schools = schools.filter(name__icontains=name)
    
    if boards:
        schools = schools.filter(board__in=boards)
    
    if grade:
        schools = schools.filter(grades_offered__icontains=grade)
    
    if ratings:
        # Filter by exact star ratings (e.g., 2* means rating >= 2.0 and < 3.0)
        rating_conditions = Q()
        for rating in ratings:
            try:
                rating_int = int(rating)
                if 1 <= rating_int <= 5:
                    # Match ratings in the range [rating_int, rating_int + 1)
                    rating_conditions |= Q(rating__gte=rating_int) & Q(rating__lt=rating_int + 1.0)
            except (ValueError, TypeError):
                pass
        if rating_conditions:
            schools = schools.filter(rating_conditions)
    
    if bus_availability:
        if 'yes' in bus_availability and 'no' not in bus_availability:
            schools = schools.filter(bus_availability=True)
        elif 'no' in bus_availability and 'yes' not in bus_availability:
            schools = schools.filter(bus_availability=False)
        # If both yes and no are selected, show all (no filter)
    
    if co_ed_types:
        schools = schools.filter(co_ed_type__in=co_ed_types)
    
    # Evaluate queryset and calculate distances if user pin code is provided
    schools_list = list(schools)
    
    # Calculate distances from user's location for each school
    if user_pin_code:
        for school in schools_list:
            distance = calculate_distance(user_pin_code, school.pin_code)
            school.calculated_distance = round(distance, 1) if distance else None
            school.default_fee = school.get_default_fee()
    else:
        for school in schools_list:
            school.calculated_distance = None
            school.default_fee = school.get_default_fee()
    
    # Filter by distance if distance_max is provided and user pin code is provided
    if distance_max and user_pin_code:
        try:
            max_distance = float(distance_max)
            filtered_schools = []
            for school in schools_list:
                if school.calculated_distance is not None and school.calculated_distance <= max_distance:
                    filtered_schools.append(school)
            schools_list = filtered_schools
        except (ValueError, TypeError):
            pass
    
    # Sort results
    sort_by = request.GET.get('sort', 'rating')
    if sort_by == 'fees':
        schools_list = sorted(schools_list, key=lambda s: s.default_fee if s.default_fee else float('inf'))
    else:
        schools_list = sorted(schools_list, key=lambda s: (float(s.rating) if s.rating else 0, s.name), reverse=True)
    
    context = {
        'schools': schools_list,
        'schools_count': len(schools_list),
        'board_choices': School.BOARD_CHOICES,
        'user_pin_code': user_pin_code,
    }
    return render(request, 'search_results.html', context)


def school_detail_view(request, school_id):
    """School detail page"""
    school = get_object_or_404(School.objects.prefetch_related('facilities'), pk=school_id)
    reviews = Review.objects.filter(school=school).order_by('-created_at')
    
    # Calculate rating distribution efficiently in one query
    rating_dist_data = reviews.values('rating').annotate(count=Count('id')).order_by('-rating')
    rating_dist = {i: 0 for i in range(1, 6)}
    total_reviews = 0
    for item in rating_dist_data:
        rating_dist[item['rating']] = item['count']
        total_reviews += item['count']
    
    # Use review_count from model if available, otherwise use count from reviews
    display_review_count = school.review_count if school.review_count > 0 else total_reviews
    
    # Convert to list of tuples for easier template iteration
    rating_dist_list = [(i, rating_dist[i], rating_dist[i] / total_reviews * 100 if total_reviews > 0 else 0) 
                        for i in range(5, 0, -1)]
    
    # Get average rating - use school.rating if available and no reviews in DB
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or (school.rating if school.rating > 0 else 0)
    
    # Pre-calculate fee
    school.default_fee = school.get_default_fee()
    
    context = {
        'school': school,
        'reviews': reviews[:10],  # Show first 10 reviews
        'rating_distribution': rating_dist,
        'rating_distribution_list': rating_dist_list,
        'total_reviews': total_reviews,
        'display_review_count': display_review_count,
        'average_rating': round(avg_rating, 1) if avg_rating else school.rating,
    }
    return render(request, 'school_detail.html', context)


def ai_picker_view(request):
    """AI Picker page"""
    # List of all countries in the world
    all_countries = [
        'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda',
        'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain',
        'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia',
        'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso',
        'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Central African Republic',
        'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica', 'Croatia',
        'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic',
        'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini',
        'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana',
        'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras',
        'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy',
        'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kosovo', 'Kuwait',
        'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein',
        'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta',
        'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco',
        'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal',
        'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'North Macedonia',
        'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay',
        'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda',
        'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino',
        'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone',
        'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Korea',
        'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria',
        'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad and Tobago',
        'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates',
        'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City', 'Venezuela',
        'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe'
    ]
    
    context = {
        'all_countries': all_countries,
    }
    return render(request, 'ai_picker.html', context)
