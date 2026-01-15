from django.urls import path
from . import views

app_name = 'announcement'

urlpatterns = [
    path('create/', views.create_announcement, name='create'),
    path('list/', views.announcement_list, name='list'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('favorites/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    path('my/', views.user_announcements, name='user_list'),
    path('<int:pk>/', views.announcement_detail, name='detail'),
    path('edit/<int:pk>/', views.edit_announcement, name='edit'),
    path('archive/<int:pk>/', views.archive_announcement, name='archive'),
    path('delete/<int:pk>/', views.delete_announcement, name='delete'),
]
