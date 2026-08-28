from django.urls import path
from . import views

urlpatterns = [
    path('', views.voice_home, name='voice_home'),
    path('process/', views.process_voice, name='process_voice'),
]