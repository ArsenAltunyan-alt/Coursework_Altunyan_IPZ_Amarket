from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
     path('', views.chat_index, name='index'),
     path('partials/list/', views.chat_list, name='list'),
     path('start/<str:username>/', views.start_chat, name='start'),
     path('chat/<str:room_name>/', views.chat_room, name='room'),
     path('chat/<str:room_name>/delete/', views.delete_chat, name='delete'),
]
