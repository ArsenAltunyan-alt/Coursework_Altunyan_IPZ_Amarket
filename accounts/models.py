from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Номер телефону",
        help_text="Введіть номер телефону"
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Місто",
        help_text="Введіть ваше місто"
    )
    
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        verbose_name="Фото профілю",
        help_text="Завантажте фото профілю"
    )
    
    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"
    
    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"
