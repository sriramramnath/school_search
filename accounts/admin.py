from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'role', 'verified']
    list_filter = ['role', 'verified']
    search_fields = ['name', 'email']
