from django.urls import path, include
from . import views


urlpatterns = [
    path('new/', views.create, name='create'),
    path('delete/<int:id>/', views.delete),
    path('update/response/add/<int:id>/', views.add_response),
]
