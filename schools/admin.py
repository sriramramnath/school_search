from django.contrib import admin
from .models import School, Facility, Review


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'location', 'rating', 'bus_availability']
    list_filter = ['board', 'co_ed_type', 'bus_availability']
    search_fields = ['name', 'location', 'pin_code']
    filter_horizontal = ['facilities']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'pin_code', 'image')
        }),
        ('Academic Details', {
            'fields': ('board', 'syllabus', 'grades_offered', 'co_ed_type')
        }),
        ('Location & Transport', {
            'fields': ('distance', 'bus_availability')
        }),
        ('Fees & Facilities', {
            'fields': ('fees_by_grade', 'facilities')
        }),
        ('Websites', {
            'fields': ('website', 'curriculum_website')
        }),
        ('Rating', {
            'fields': ('rating',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer_name', 'school', 'rating', 'verified', 'created_at']
    list_filter = ['rating', 'verified', 'created_at']
    search_fields = ['reviewer_name', 'school__name', 'comment']
    readonly_fields = ['created_at']
