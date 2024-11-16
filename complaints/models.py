from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User


cipher = Fernet(settings.ENCRYPTION_KEY)

class Complaint(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    category = models.TextField(null=False, blank=False)
    is_anonymous = models.BooleanField(default=False)
    email_for_reply = models.EmailField(blank=True, null=True)
    reply_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=[('open', 'Open'), ('closed', 'Closed')], default='open')
    ip_address = models.CharField(max_length=255)
    device_identifier = models.CharField(max_length=255)
    is_spam = models.BooleanField(default=False)
    needs_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def set_ip_address(self, value):
        self.ip_address = cipher.encrypt(value.encode()).decode()

    def get_ip_address(self):
        return cipher.decrypt(self.ip_address.encode()).decode()


    def set_device_identifier(self, value):
        self.device_identifier = cipher.encrypt(value.encode()).decode()

    def get_device_identifier(self):
        return cipher.decrypt(self.device_identifier.encode()).decode()

    def __str__(self):
        return f"Complaint {self.id}"



class ComplaintLike(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ComplaintResponse(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    response_text = models.TextField()
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
