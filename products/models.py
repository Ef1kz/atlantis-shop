from django.db import models

class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    collection = models.CharField("Коллекция", max_length=100, blank=True)
    color = models.CharField("Цвет", max_length=50, blank=True)
    width = models.DecimalField("Ширина (см)", max_digits=6, decimal_places=1, null=True, blank=True)
    height = models.DecimalField("Высота (см)", max_digits=6, decimal_places=1, null=True, blank=True)
    depth = models.DecimalField("Глубина (см)", max_digits=6, decimal_places=1, null=True, blank=True)
    image = models.ImageField("Изображение", upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return self.name