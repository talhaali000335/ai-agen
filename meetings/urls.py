from django.urls import path
from . import views

urlpatterns = [
    path('', views.meetings_home, name='meetings_home'),
    path('upload/', views.upload_meeting, name='upload_meeting'),
    path('<uuid:meeting_id>/', views.meeting_detail, name='meeting_detail'),
]