from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.auth, name='auth'),
    path('auth/code/send/', views.send_code),
    path('auth/code/check/', views.check_code),
    path('complaints/create/', views.create_complaint, name='create_complaint'),
    path('blocked/', views.blocked, name='blocked'),
    path('complaints/my/', views.my_complaints, name='my_complaints'),
    path('exit/', views.exit, name='exit'),
    path('loadmore/', views.loadmore, name='loadmore'),
]
