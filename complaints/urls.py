from django.urls import path, include
from . import views


urlpatterns = [
    path('new/', views.create, name='create'),
    path('delete/<int:id>/', views.delete),
    path('public/delete/<int:id>/', views.delete_public),
    path('update/response/add/<int:id>/', views.add_response),
    path('like/', views.like, name='like'),
    path('unlike/', views.unlike, name='unlike'),
    path('<str:key>/', views.complaint, name='complaint'),
]
