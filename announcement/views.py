import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import AnnouncementForm, AnnouncementImageForm
from .models import Announcement, AnnouncementImage, Category
from django.contrib import messages
from django.db.models import F, Q, Max

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
        'categories': categories,
        'main_existing_image_id': '',
    })

def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    Announcement.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
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
        image_form = AnnouncementImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            delete_ids = request.POST.getlist('delete_images')
            if delete_ids:
                AnnouncementImage.objects.filter(announcement=announcement, id__in=delete_ids).delete()

            images = request.FILES.getlist('images')
            main_image_index = 0
            try:
                main_image_index = int(request.POST.get('main_image_index', 0))
            except ValueError:
                pass

            main_existing_id = request.POST.get('main_existing_image_id') or ''

            if len(images) > 10:
                messages.error(request, '????? ??????????? ???????? 10 ????.')
                categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories').order_by('name')
                main_existing_image_id = AnnouncementImage.objects.filter(announcement=announcement, is_main=True).values_list('id', flat=True).first()
                return render(request, 'announcement/create_announcement.html', {
                    'form': form,
                    'image_form': image_form,
                    'is_edit': True,
                    'announcement': announcement,
                    'categories': categories,
                    'main_existing_image_id': main_existing_image_id or '',
                })

            if images:
                if 0 <= main_image_index < len(images):
                    AnnouncementImage.objects.filter(announcement=announcement, is_main=True).update(is_main=False)

                for i, image in enumerate(images):
                    is_main = (i == main_image_index)
                    AnnouncementImage.objects.create(
                        announcement=announcement,
                        image=image,
                        is_main=is_main
                    )

            if main_existing_id:
                existing_main = AnnouncementImage.objects.filter(announcement=announcement, id=main_existing_id).first()
                if existing_main:
                    AnnouncementImage.objects.filter(announcement=announcement, is_main=True).update(is_main=False)
                    existing_main.is_main = True
                    existing_main.save()

            if not AnnouncementImage.objects.filter(announcement=announcement, is_main=True).exists():
                first_image = AnnouncementImage.objects.filter(announcement=announcement).first()
                if first_image:
                    first_image.is_main = True
                    first_image.save()

            messages.success(request, 'Оголошення успішно оновлено!')
            return redirect('announcement:user_list')
    else:
        form = AnnouncementForm(instance=announcement)
        image_form = AnnouncementImageForm()
    
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories').order_by('name')
    main_existing_image_id = AnnouncementImage.objects.filter(announcement=announcement, is_main=True).values_list('id', flat=True).first()
    return render(request, 'announcement/create_announcement.html', {
        'form': form,
        'image_form': image_form,
        'is_edit': True,
        'announcement': announcement,
        'categories': categories,
        'main_existing_image_id': main_existing_image_id or '',
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
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories').order_by('name')
    max_price_value = Announcement.objects.filter(
        is_active=True,
        price__isnull=False,
    ).aggregate(Max('price'))['price__max'] or 0
    
    selected_category_parent_ids = set()
    # Filter by Category (support multiple selections)
    category_slugs = [slug for slug in request.GET.getlist('category') if slug]
    if category_slugs:
        categories_qs = Category.objects.filter(slug__in=category_slugs)
        for category in categories_qs:
            selected_category_parent_ids.add(category.parent_id or category.id)

        parent_ids = [c.id for c in categories_qs if c.parent_id is None]
        child_ids = [c.id for c in categories_qs if c.parent_id is not None]
        category_filter = Q()

        if parent_ids:
            parent_filter = Category.objects.filter(parent_id__in=parent_ids)
            category_filter |= Q(category__in=Category.objects.filter(Q(id__in=parent_ids) | Q(id__in=parent_filter)))

        if child_ids:
            category_filter |= Q(category_id__in=child_ids)

        announcements = announcements.filter(category_filter)

    # Filter by Seller
    seller_username = request.GET.get('seller')
    if seller_username:
        announcements = announcements.filter(seller__username=seller_username)
    
    # Filter by Price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price == '0' and max_price == '0':
        announcements = announcements.filter(Q(price__isnull=True) | Q(price=0))
    else:
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
        'condition_choices': Announcement.CONDITION_CHOICES,
        'selected_categories': category_slugs,
        'selected_category_parent_ids': sorted(selected_category_parent_ids),
        'selected_condition': condition or '',
        'min_price': min_price or '',
        'max_price': max_price or '',
        'is_negotiable_selected': is_negotiable == 'on',
        'total_count': announcements.count(),
        'max_price_value': max_price_value,
    }
    if request.headers.get("HX-Request") == "true":
        return render(request, 'announcement/partials/announcement_cards.html', context)
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
        message_text = 'Оголошення видалено з обраного.'
        is_favorite = False
    else:
        announcement.favorites.add(request.user)
        message_text = 'Оголошення додано до обраного.'
        is_favorite = True

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "message": message_text,
            "is_favorite": is_favorite,
        })

    messages.success(request, message_text)

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('announcement:detail', pk=announcement.pk)

def load_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Category.objects.filter(parent_id=category_id).order_by('name')
    return JsonResponse(list(subcategories.values('id', 'name')), safe=False)


def _generate_description_from_title(title):
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    prompt = f"""
        Створи короткий опис для оголошення "{title}" українською мовою.

        Структура:
        1. Вступ (1 речення) — що це за товар/послуга
        2. Опис (2–3 речення) — загальна корисна інформація
        3. Наприкінці — окремий список з 3–5 параметрів у новому рядку

        Формат параметрів (ОБОВʼЯЗКОВО):
        Назва параметра: [вкажіть параметр]

        ! Заборонено:
        - писати плейсхолдери без назви параметра
        - змінювати формат дужок або текст усередині
        - додавати маркери, тире або нумерацію

        Приклад правильного формату:
        Пробіг: [вкажіть пробіг]
        Коробка передач: [вкажіть коробку передач]

        Плейсхолдери залежно від типу оголошення:
        - Нерухомість: площа, кількість кімнат, поверх, стан, ціна за м²
        - Транспорт (авто/мото): рік, пробіг, стан, коробка передач, обʼєм двигуна
        - Електроніка: стан, модель, комплектація, гарантія, причина продажу
        - Робота: досвід, графік, зарплата, вимоги, обовʼязки
        - Послуги: вартість, тривалість, досвід, умови, виїзд
        - Дім і сад: розміри, матеріал, стан, колір, доставка
        - Мода: розмір, стан, бренд, матеріал, колір
        - Дитячі товари: вік, стан, бренд, комплектація
        - Хобі і спорт: стан, бренд, розмір/вага, комплектація
        - Тварини: вік, порода, стать, документи, щеплення
        - Бізнес: тип діяльності, дохід, причина продажу, персонал

        Правила:
        - Тон нейтральний, без реклами та оцінних суджень
        - Не вигадуй цифри, роки, потужність або характеристики
        - Обирай лише найважливіші 3–5 параметрів
        - Загальний обсяг — не більше 100–120 слів
        """


    model = settings.OPENROUTER_MODEL
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    if settings.OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
    if settings.OPENROUTER_APP_NAME:
        headers["X-Title"] = settings.OPENROUTER_APP_NAME

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"OpenRouter response missing choices: {data}")

    message = choices[0].get("message", {}) or {}
    text = message.get("content")
    if not text:
        text = message.get("reasoning")

    if not text:
        raise RuntimeError(f"OpenRouter response did not include text. Raw: {data}")

    return str(text).strip()


@login_required
@require_POST
def generate_description_from_title(request):
    title = request.POST.get("title", "").strip()
    if not title:
        return JsonResponse({"error": "Title is required."}, status=400)

    try:
        description = _generate_description_from_title(title)
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else 502
        details = exc.response.text if exc.response is not None else str(exc)
        return JsonResponse(
            {"error": "AI service request failed.", "details": details},
            status=status_code,
        )
    except requests.RequestException as exc:
        return JsonResponse({"error": "AI service request failed.", "details": str(exc)}, status=502)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse({"description": description})
