from django.shortcuts import render

def home(request):
    """
    Renders the home page.
    """
    return render(request, 'main/home.html')
