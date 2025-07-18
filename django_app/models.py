from django.db import models
from django.contrib.auth.models import User

class Docs(models.Model):
    file_path = models.CharField(max_length=255, verbose_name="Путь к файлу")
    size = models.FloatField(verbose_name="Размер (КБ)")
    fastapi_id = models.PositiveIntegerField(verbose_name="FastAPI ID")

    def __str__(self):
        return f"Док #{self.id} (FastAPI {self.fastapi_id})"

class UsersToDocs(models.Model):
    username = models.CharField(max_length=100, verbose_name="Имя пользователя")
    docs = models.ForeignKey(Docs, on_delete=models.CASCADE, verbose_name="Документ")

    def __str__(self):
        return f"{self.username} -> Док #{self.docs.id}"

class Price(models.Model):
    file_type = models.CharField(max_length=10, verbose_name="Тип файла")
    price = models.FloatField(verbose_name="Цена за 1 КБ")

    def __str__(self):
        return f"{self.file_type}: {self.price} руб/КБ"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    docs = models.ForeignKey(Docs, on_delete=models.CASCADE, verbose_name="Документ")
    order_price = models.FloatField(verbose_name="Стоимость заказа")
    payment = models.BooleanField(default=False, verbose_name="Оплачено")

    def __str__(self):
        return f"Заказ #{self.id}"