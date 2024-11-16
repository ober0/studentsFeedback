from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


cipher = Fernet(settings.ENCRYPTION_KEY)


class UserUnbanRequest(models.Model):
    ip_address = models.CharField(max_length=255, verbose_name='IP-адрес')
    device_identifier = models.CharField(max_length=255, verbose_name='Идентификатор устройства')
    complaint = models.ForeignKey('complaints.Complaint', on_delete=models.CASCADE, null=False, blank=False, verbose_name='Жалоба')
    request_text = models.TextField(verbose_name='Текст запроса')
    review_result = models.CharField(
        max_length=50,
        choices=[('unbanned', 'Разбанен'), ('rejected', 'Отклонен')],
        blank=True,
        null=True,
        verbose_name='Результат рассмотрения'
    )
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Рассмотрено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def set_ip_address(self, value):
        self.ip_address = cipher.encrypt(value.encode()).decode()

    def get_ip_address(self):
        return cipher.decrypt(self.ip_address.encode()).decode()

    def set_device_identifier(self, value):
        self.device_identifier = cipher.encrypt(value.encode()).decode()

    def get_device_identifier(self):
        return cipher.decrypt(self.device_identifier.encode()).decode()

    class Meta:
        verbose_name = 'Запрос на разбан'
        verbose_name_plural = 'Запросы на разбан'


class BlockedUser(models.Model):
    ip_address = models.CharField(max_length=255, verbose_name='IP-адрес')
    device_identifier = models.CharField(max_length=255, verbose_name='Идентификатор устройства')
    block_reason = models.TextField(verbose_name='Причина блокировки')
    blocked_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата блокировки')

    def set_ip_address(self, value):
        self.ip_address = cipher.encrypt(value.encode()).decode()

    def get_ip_address(self):
        return cipher.decrypt(self.ip_address.encode()).decode()

    def set_device_identifier(self, value):
        self.device_identifier = cipher.encrypt(value.encode()).decode()

    def get_device_identifier(self):
        return cipher.decrypt(self.device_identifier.encode()).decode()

    class Meta:
        verbose_name = 'Заблокированный пользователь'
        verbose_name_plural = 'Заблокированные пользователи'
