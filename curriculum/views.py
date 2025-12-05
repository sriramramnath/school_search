from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Curriculum
from .utils import get_wikipedia_data, search_wikipedia_page_title


def curriculum_search_view(request):
    """Curriculum search page"""
    curricula = Curriculum.objects.all()
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        curricula = curricula.filter(
            Q(name__icontains=search_query) |
            Q(abbreviation__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'curricula': curricula,
        'search_query': search_query,
    }
    return render(request, 'curriculum_search.html', context)


def curriculum_detail_view(request, curriculum_id):
    """Curriculum detail page with Wikipedia integration"""
    curriculum = get_object_or_404(Curriculum, pk=curriculum_id)
    
    # Fetch Wikipedia data
    wikipedia_data = None
    search_term = curriculum.get_wikipedia_search_term()
    
    if curriculum.wikipedia_page:
        # Use stored Wikipedia page title
        wikipedia_data = get_wikipedia_data(page_title=curriculum.wikipedia_page)
    else:
        # Try to auto-detect Wikipedia page
        page_title = search_wikipedia_page_title(curriculum.name, curriculum.abbreviation)
        if page_title:
            wikipedia_data = get_wikipedia_data(page_title=page_title)
    
    # If still no data, try with search term
    if not wikipedia_data:
        wikipedia_data = get_wikipedia_data(search_term=search_term)
    
    context = {
        'curriculum': curriculum,
        'wikipedia_data': wikipedia_data,
    }
    return render(request, 'curriculum_detail.html', context)
