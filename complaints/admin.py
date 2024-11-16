from django.contrib import admin
from .models import Complaint, ComplaintLike

admin.site.register(Complaint)
admin.site.register(ComplaintLike)