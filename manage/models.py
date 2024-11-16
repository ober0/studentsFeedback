from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


cipher = Fernet(settings.ENCRYPTION_KEY)


class UserUnbanRequest(models.Model):
    ip_address = models.CharField(max_length=255)
    device_identifier = models.CharField(max_length=255)
    complaint = models.ForeignKey('complaints.Complaint', on_delete=models.CASCADE, null=False, blank=False)
    request_text = models.TextField()
    review_result = models.CharField(max_length=50, choices=[('unbanned', 'Unbanned'), ('rejected', 'Rejected')], blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_ip_address(self, value):
        self.ip_address = cipher.encrypt(value.encode()).decode()

    def get_ip_address(self):
        return cipher.decrypt(self.ip_address.encode()).decode()


    def set_device_identifier(self, value):
        self.device_identifier = cipher.encrypt(value.encode()).decode()

    def get_device_identifier(self):
        return cipher.decrypt(self.device_identifier.encode()).decode()



class BlockedUser(models.Model):
    ip_address = models.CharField(max_length=255)
    device_identifier = models.CharField(max_length=255)
    block_reason = models.TextField()
    blocked_at = models.DateTimeField(auto_now_add=True)


    def set_ip_address(self, value):
        self.ip_address = cipher.encrypt(value.encode()).decode()

    def get_ip_address(self):
        return cipher.decrypt(self.ip_address.encode()).decode()


    def set_device_identifier(self, value):
        self.device_identifier = cipher.encrypt(value.encode()).decode()

    def get_device_identifier(self):
        return cipher.decrypt(self.device_identifier.encode()).decode()