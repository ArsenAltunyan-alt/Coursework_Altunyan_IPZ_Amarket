from django.urls import path
from . import views

app_name = "assistant"

urlpatterns = [
    path("message/", views.assistant_message, name="message"),
]
