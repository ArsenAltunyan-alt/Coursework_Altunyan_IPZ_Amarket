from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import AnnouncementForm, AnnouncementImageForm
from .models import Announcement, AnnouncementImage, Category
from django.contrib import messages
from django.db.models import F, Q

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
    
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories').order_by('name')
    
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

    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(
            request.user.favorite_announcements.values_list('id', flat=True)
        )

    return render(request, 'announcement/announcement_detail.html', {
        'announcement': announcement,
        'favorite_ids': favorite_ids,
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
    
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories').order_by('name')
    return render(request, 'announcement/create_announcement.html', {
        'form': form,
        'is_edit': True,
        'categories': categories,
    })

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
        selected_category = Category.objects.filter(slug=category_slug).first()
        if selected_category:
            if selected_category.parent_id is None:
                announcements = announcements.filter(
                    category__in=Category.objects.filter(Q(pk=selected_category.pk) | Q(parent=selected_category))
                )
            else:
                announcements = announcements.filter(category=selected_category)

    # Filter by Seller
    seller_username = request.GET.get('seller')
    if seller_username:
        announcements = announcements.filter(seller__username=seller_username)
    
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

    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(
            request.user.favorite_announcements.values_list('id', flat=True)
        )

    context = {
        'announcements': announcements,
        'categories': categories,
        'favorite_ids': favorite_ids,
    }
    return render(request, 'announcement/announcement_list.html', context)

@login_required
def favorites_list(request):
    announcements = Announcement.objects.filter(
        favorites=request.user,
        is_active=True,
    ).order_by('-created_at')
    return render(request, 'announcement/favorite_list.html', {
        'announcements': announcements,
    })


@login_required
def toggle_favorite(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk, is_active=True)
    if announcement.favorites.filter(pk=request.user.pk).exists():
        announcement.favorites.remove(request.user)
        messages.success(request, 'Оголошення видалено з обраного.')
    else:
        announcement.favorites.add(request.user)
        messages.success(request, 'Оголошення додано до обраного.')

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('announcement:detail', pk=announcement.pk)

def load_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Category.objects.filter(parent_id=category_id).order_by('name')
    return JsonResponse(list(subcategories.values('id', 'name')), safe=False)
