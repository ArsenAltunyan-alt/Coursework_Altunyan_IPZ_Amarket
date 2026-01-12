from django.shortcuts import render
from announcement.models import Announcement

def home(request):
    """
    Renders the home page.
    """
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'main/home.html', {'announcements': announcements})
