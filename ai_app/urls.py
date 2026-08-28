from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),          # serves the chat page at "/"
    path('chat/', views.chat, name='chat'),
    path('conversations/', views.list_conversations, name='conversations'),
]