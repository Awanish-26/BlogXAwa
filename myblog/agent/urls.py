from . import views
from django.urls import path

urlpatterns = [
    path("chat/", views.chatbot, name="chatbot")
]
