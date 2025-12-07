from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import Curriculum


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
    
    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        results = []
        for curriculum in curricula:
            results.append({
                'id': curriculum.id,
                'name': curriculum.name,
                'abbreviation': curriculum.abbreviation or '',
                'description': curriculum.description or '',
                'url': curriculum.get_absolute_url() if hasattr(curriculum, 'get_absolute_url') else f'/curriculum/{curriculum.id}/',
            })
        return JsonResponse({'curricula': results})
    
    context = {
        'curricula': curricula,
        'search_query': search_query,
    }
    return render(request, 'curriculum_search.html', context)


def curriculum_detail_view(request, curriculum_id):
    """Curriculum detail page"""
    curriculum = get_object_or_404(Curriculum, pk=curriculum_id)
    
    context = {
        'curriculum': curriculum,
    }
    return render(request, 'curriculum_detail.html', context)
