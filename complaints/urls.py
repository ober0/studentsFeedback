from django.urls import path, include
from . import views


urlpatterns = [
    path('new/', views.create, name='create'),


]
