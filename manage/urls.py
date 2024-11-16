from django.urls import path, include
from . import views


urlpatterns = [
    path('check_fingerprint/', views.check_fingerprint)
]
