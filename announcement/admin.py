from django.contrib import admin
from .models import Announcement, AnnouncementImage, Category

class AnnouncementImageInline(admin.TabularInline):
    model = AnnouncementImage
    extra = 1

class CategoryInline(admin.TabularInline):
    model = Category
    fk_name = 'parent'
    extra = 1

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    inlines = [AnnouncementImageInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'requires_condition')
    list_filter = ('parent', 'requires_condition')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CategoryInline]
