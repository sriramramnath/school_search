from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('search/', views.school_search_view, name='school_search'),
    path('search/results/', views.school_search_results_view, name='school_search_results'),
    path('school/<int:school_id>/', views.school_detail_view, name='school_detail'),
]



