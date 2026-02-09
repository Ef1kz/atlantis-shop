# products/admin.py
from django.contrib import admin
from .models import Product, Category  # Только те модели, которые существуют

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'category', 'created_at']
    list_filter = ['available', 'category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'available']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}