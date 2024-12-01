import secrets
from django.db import models
from django.contrib.auth.models import User

class Complaint(models.Model):
    user = models.ForeignKey('core.Students', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    content = models.TextField(verbose_name='Содержание')
    category = models.TextField(null=False, blank=False, verbose_name='Категория')
    user_name = models.CharField(max_length=100, blank=True, null=True)
    user_group = models.CharField(max_length=100, blank=True, null=True)
    is_anonymous = models.BooleanField(default=False, verbose_name='Анонимно')
    email_for_reply = models.EmailField(blank=True, null=True, verbose_name='Email для ответа')
    reply_code = models.CharField(max_length=100, unique=False, blank=False, null=False, verbose_name='Код жалобы', default=secrets.token_hex(32))
    is_public = models.BooleanField(default=False, verbose_name='Публичная')
    is_published = models.BooleanField(default=False, verbose_name='Опубликована')
    status = models.CharField(max_length=50, choices=[('open', 'Открыта'), ('closed', 'Закрыта')], default='open', verbose_name='Статус')
    ip_address = models.CharField(max_length=255, verbose_name='IP-адрес')
    device_identifier = models.CharField(max_length=255, verbose_name='Идентификатор устройства')
    is_spam = models.BooleanField(default=False, verbose_name='Является спамом')
    needs_review = models.BooleanField(default=False, verbose_name='Требует проверки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    response_text = models.TextField(verbose_name='Текст ответа', null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Администратор')


    def __str__(self):
        return f"Обращение {self.id}"

    class Meta:
        verbose_name = 'Обращени'
        verbose_name_plural = 'Обращения'


class ComplaintLike(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, null=False, blank=False, verbose_name='Обращение')
    user = models.ForeignKey('core.Students', on_delete=models.CASCADE, null=False, blank=False, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Лайк на обращение'
        verbose_name_plural = 'Лайки на обращения'

