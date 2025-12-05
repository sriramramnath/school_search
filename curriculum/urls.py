from django.urls import path
from . import views

urlpatterns = [
    path('', views.curriculum_search_view, name='curriculum_search'),
    path('<int:curriculum_id>/', views.curriculum_detail_view, name='curriculum_detail'),
]


