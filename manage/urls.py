from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='manage'),
    path('check_fingerprint/', views.check_fingerprint),
    path('unban/request/', views.unban_request),
    path('complaint/load/', views.load_banned_complaint),
    path('complaint/open/', views.open_complaints, name='open_complaints'),
    path('complaint/open/need_review/', views.open_need_review_complaints, name='open_need_review_complaints'),
    path('complaint/close/', views.close_complaints, name='close_complaints'),
    path('complaint/<int:id>/', views.complaint),
    path('ban/<int:id>/', views.ban),
]
