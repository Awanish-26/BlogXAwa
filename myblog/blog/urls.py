from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/edit/', views.edit, name='edit'),
    path('post/<int:pk>/delete/', views.delete, name='delete'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/publish/', views.publish_post, name='publish_post'),
    path('post/<int:pk>/unpublish/', views.unpublish_post, name='unpublish_post'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/comment/', views.comment_create, name='comment_create'),
    path('comment/<int:pk>/edit/', views.comment_edit, name='comment_edit'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('post/<int:pk>/<slug:slug>/', views.post_detail, name='post_detail'),
]
