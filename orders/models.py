from django.db import models
from django.conf import settings  # ← Добавить импорт
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    class Meta:
        verbose_name = 'заказ'  # Единичное
        verbose_name_plural = 'заказы'  # Множественное (будет в sidebar)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Исправлено
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Поля для доставки
    delivery_address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"Order #{self.id} by {self.user if self.user else 'Guest'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"
    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'  # Переведённый "Order items"