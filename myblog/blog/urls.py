from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/edit/', views.edit, name='edit'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/delete/', views.delete, name='delete'),
    path('share/<int:pk>/', views.post_share, name='post_share'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
]
