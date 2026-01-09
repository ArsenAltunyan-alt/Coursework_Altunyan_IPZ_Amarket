from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Адмін панель для кастомної моделі користувача"""
    
    list_display = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'city', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'city']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {
            'fields': ('phone_number', 'city', 'profile_photo')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Додаткова інформація', {
            'fields': ('first_name', 'last_name', 'phone_number', 'city', 'profile_photo')
        }),
    )