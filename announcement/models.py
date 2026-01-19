from django.db import models
from django.conf import settings

class Announcement(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcements')
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favorite_announcements', blank=True)
    title = models.CharField(max_length=255, verbose_name='Назва')
    description = models.TextField(verbose_name='Опис')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Ціна')
    is_negotiable = models.BooleanField(default=False, verbose_name='Можливість торгу')
    address = models.CharField(max_length=255, verbose_name='Адреса')
    is_active = models.BooleanField(default=True, verbose_name='Активне')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Переглядів')
    
    # Geolocation
    latitude = models.FloatField(null=True, blank=True, verbose_name='Широта')
    longitude = models.FloatField(null=True, blank=True, verbose_name='Довгота')
    
    CONDITION_CHOICES = [
        ('', 'Не обрано'),
        ('new', 'Новий'),
        ('used', 'Б/В'),
    ]
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, null=True, blank=True, verbose_name='Стан')
    category = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='announcements', verbose_name='Категорія', null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_main_image(self):
        main_img = self.images.filter(is_main=True).first()
        if main_img:
            return main_img.image
        first_img = self.images.first()
        if first_img:
            return first_img.image
        return None

    class Meta:
        verbose_name = 'Оголошення'
        verbose_name_plural = 'Оголошення'

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Назва')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subcategories',
        on_delete=models.PROTECT,
        verbose_name='Parent category',
    )
    requires_condition = models.BooleanField(default=True, verbose_name='Потребує вказання стану')

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def get_full_name(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name

    def __str__(self):
        return self.get_full_name()

class AnnouncementImage(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='announcements/', verbose_name='Зображення')
    is_main = models.BooleanField(default=False, verbose_name='Головне фото')

    def __str__(self):
        return f"Image for {self.announcement.title}"
