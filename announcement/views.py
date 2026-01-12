from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AnnouncementForm, AnnouncementImageForm
from .models import Announcement, AnnouncementImage, Category
from django.contrib import messages
from django.db.models import F

@login_required
def create_announcement(request):
    if request.method == 'POST':
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        form = AnnouncementForm(request.POST)
        image_form = AnnouncementImageForm(request.POST, request.FILES)
        
        if form.is_valid() and image_form.is_valid():
            announcement = form.save(commit=False)
        else:
            print("Form errors:", form.errors)
            print("Image form errors:", image_form.errors)
        
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.seller = request.user
            announcement.save()
            
            images = request.FILES.getlist('images')
            main_image_index = 0
            try:
                main_image_index = int(request.POST.get('main_image_index', 0))
            except ValueError:
                pass
            
            if len(images) > 10:
                messages.error(request, 'Можна завантажити максимум 10 фото.')
                announcement.delete() 
                return render(request, 'announcement/create_announcement.html', {'form': form, 'image_form': image_form})

            for i, image in enumerate(images):
                is_main = (i == main_image_index)
                AnnouncementImage.objects.create(
                    announcement=announcement,
                    image=image,
                    is_main=is_main
                )
                
            messages.success(request, 'Оголошення успішно створено!')
            return redirect('announcement:list')
    else:
        form = AnnouncementForm()
        image_form = AnnouncementImageForm()
    
    image_form = AnnouncementImageForm()
    
    categories = Category.objects.all()
    
    return render(request, 'announcement/create_announcement.html', {
        'form': form, 
        'image_form': image_form,
        'categories': categories
    })

def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    # Increment views count atomically
    Announcement.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
    # Reload for template to show new count
    announcement.refresh_from_db()
    
    return render(request, 'announcement/announcement_detail.html', {
        'announcement': announcement,
    })

@login_required
def user_announcements(request):
    announcements = Announcement.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'announcement/user_announcements.html', {'announcements': announcements})

@login_required
def edit_announcement(request, pk):
    announcement = Announcement.objects.get(pk=pk)
    if announcement.seller != request.user:
        return redirect('announcement:list')
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Оголошення оновлено!')
            return redirect('announcement:user_list')
    else:
        form = AnnouncementForm(instance=announcement)
    
    return render(request, 'announcement/create_announcement.html', {'form': form, 'is_edit': True})

@login_required
def archive_announcement(request, pk):
    announcement = Announcement.objects.get(pk=pk)
    if announcement.seller == request.user:
        announcement.is_active = not announcement.is_active
        announcement.save()
        status = "архівовано" if not announcement.is_active else "відновлено"
        messages.success(request, f'Оголошення {status}!')
    return redirect('announcement:user_list')

@login_required
def delete_announcement(request, pk):
    announcement = Announcement.objects.get(pk=pk)
    if announcement.seller == request.user:
        announcement.delete()
        messages.success(request, 'Оголошення видалено!')
    return redirect('announcement:user_list')

def announcement_list(request):
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    categories = Category.objects.all()
    
    # Filter by Category
    category_slug = request.GET.get('category')
    if category_slug:
        announcements = announcements.filter(category__slug=category_slug)
    
    # Filter by Price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        announcements = announcements.filter(price__gte=min_price)
    if max_price:
        announcements = announcements.filter(price__lte=max_price)
        
    # Filter by Condition
    condition = request.GET.get('condition')
    if condition:
        announcements = announcements.filter(condition=condition)
        
    # Filter by Negotiable
    is_negotiable = request.GET.get('is_negotiable')
    if is_negotiable == 'on':
        announcements = announcements.filter(is_negotiable=True)

    context = {
        'announcements': announcements,
        'categories': categories,
    }
    return render(request, 'announcement/announcement_list.html', context)
