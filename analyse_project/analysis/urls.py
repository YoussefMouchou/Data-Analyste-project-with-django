from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Page d'accueil
    path('upload/', views.upload_file, name='Upload'),  # Changed name to 'Upload'
    path('view/', views.view_data, name='view_data'),
    path('index/', views.index_data, name='index_data'),
    path('analyze/', views.analyze_data, name='analyze'),
    path('visualize/', views.visualize_data, name='visualize'),
]
