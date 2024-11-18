from django.urls import path, include
from . import views


urlpatterns = [
    path('auto-check/', views.auto_check, name='auto_check'),
]
