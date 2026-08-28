from django.urls import path
from . import views

urlpatterns = [
    path('', views.rag_home, name='rag_home'),             # serve HTML
    path('upload/', views.upload_document, name='upload_document'),
    path('rag-chat/', views.rag_chat, name='rag_chat'),
]