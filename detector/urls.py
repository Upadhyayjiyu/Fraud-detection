"""
URL configuration for detector app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('monitoring/', views.monitoring, name='monitoring'),
    path('analytics/', views.analytics, name='analytics'),
    path('api/predict/', views.predict_transaction, name='predict'),
    path('api/stats/', views.get_statistics, name='stats'),
    path('api/load-sample/', views.load_sample_data, name='load_sample'),
]
