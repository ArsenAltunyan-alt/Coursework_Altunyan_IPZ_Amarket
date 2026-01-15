from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
     path('', views.chat_index, name='index'),
     path('start/<str:username>/', views.start_chat, name='start'),
     path('chat/<str:room_name>/', views.chat_room, name='room'),
]
