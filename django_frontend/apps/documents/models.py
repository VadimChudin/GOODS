from django.db import models
from django.contrib.auth.models import User
import os


class Docs(models.Model):
    file_path = models.CharField(max_length=500, verbose_name='Путь к файлу')
    size = models.FloatField(verbose_name='Размер файла (КБ)')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    def __str__(self):
        return f"Документ {self.id} - {os.path.basename(self.file_path)}"

    @property
    def filename(self):
        return os.path.basename(self.file_path)

    @property
    def file_extension(self):
        return os.path.splitext(self.file_path)[1].lower()


class UsersToDocs(models.Model):
    username = models.CharField(max_length=150, verbose_name='Имя пользователя')
    docs = models.ForeignKey(Docs, on_delete=models.CASCADE, verbose_name='Документ')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Связь пользователя с документом'
        verbose_name_plural = 'Связи пользователей с документами'

    def __str__(self):
        return f"{self.username} - {self.docs.filename}"


class Price(models.Model):
    file_type = models.CharField(max_length=10, unique=True, verbose_name='Тип файла')
    price = models.FloatField(verbose_name='Цена за 1 КБ')

    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'

    def __str__(self):
        return f"{self.file_type} - {self.price} руб/КБ"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    docs = models.ForeignKey(Docs, on_delete=models.CASCADE, verbose_name='Документ')
    order_price = models.FloatField(verbose_name='Цена заказа')
    payment = models.BooleanField(default=False, verbose_name='Оплачено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        unique_together = ['user', 'docs']

    def __str__(self):
        return f"Заказ {self.id} - {self.user.username} - {self.docs.filename}"
