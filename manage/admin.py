from django.contrib import admin
from .models import UserUnbanRequest, BlockedUser

admin.site.register(UserUnbanRequest)
admin.site.register(BlockedUser)