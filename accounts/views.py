from django.shortcuts import render
from .models import UserProfile


def profile_view(request):
    """User profile page (basic, no auth for now)"""
    # For now, create a default profile or get from session
    profile, created = UserProfile.objects.get_or_create(
        defaults={
            'name': 'User',
            'email': 'user@example.com',
            'role': 'Parent',
            'language': 'English US',
        }
    )
    
    context = {
        'profile': profile,
    }
    return render(request, 'profile.html', context)
