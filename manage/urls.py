from django.urls import path, include
from . import views


urlpatterns = [
    path('check_fingerprint/', views.check_fingerprint),
    path('unban/request/', views.unban_request),
    path('complaint/load/', views.load_banned_complaint),
]
