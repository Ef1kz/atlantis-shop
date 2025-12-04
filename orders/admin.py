from django.contrib import admin
from .models import Order, OrderItem
from products.models import Product  # импорт нужен, но НЕ для регистрации

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created_at', 'total_amount']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]