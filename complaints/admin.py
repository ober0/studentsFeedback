from django.contrib import admin
from .models import Complaint, ComplaintResponse, ComplaintLike

admin.site.register(Complaint)
admin.site.register(ComplaintResponse)
admin.site.register(ComplaintLike)