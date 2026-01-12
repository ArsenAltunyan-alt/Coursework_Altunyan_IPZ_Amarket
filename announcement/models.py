from django.db import models
from django.conf import settings

class Announcement(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255, verbose_name='Назва')
    description = models.TextField(verbose_name='Опис')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Ціна')
    is_negotiable = models.BooleanField(default=False, verbose_name='Можливість торгу')
    address = models.CharField(max_length=255, verbose_name='Адреса')
    is_active = models.BooleanField(default=True, verbose_name='Активне')
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

class AnnouncementImage(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='announcements/', verbose_name='Зображення')
    is_main = models.BooleanField(default=False, verbose_name='Головне фото')

    def __str__(self):
        return f"Image for {self.announcement.title}"
