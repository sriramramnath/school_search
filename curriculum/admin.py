from django.contrib import admin
from .models import Curriculum


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'website']
    search_fields = ['name', 'abbreviation', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'abbreviation', 'description')
        }),
        ('Academic Details', {
            'fields': ('subjects', 'exams', 'info')
        }),
        ('Website & Wikipedia', {
            'fields': ('website', 'wikipedia_page')
        }),
    )
