from django.contrib import admin
from .models import Announcement, AnnouncementImage, Category

class AnnouncementImageInline(admin.TabularInline):
    model = AnnouncementImage
    extra = 1

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    inlines = [AnnouncementImageInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'requires_condition')
    prepopulated_fields = {'slug': ('name',)}
