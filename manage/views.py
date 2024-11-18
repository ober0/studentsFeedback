from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import BlockedUser
from complaints.models import Complaint

# @user_passes_test(lambda u: u.is_superuser, login_url='/admin/login/')

@csrf_exempt
def check_fingerprint(request):
    if request.method == 'POST':
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        fingerprint = request.POST.get('fingerprint')
        old_fingerprint = request.POST.get('old_fingerprint')
        if old_fingerprint:
            try:
                blockedFingerprint = BlockedUser.objects.filter(device_identifier=old_fingerprint).first()
                blockedFingerprint.device_identifier = fingerprint
                blockedFingerprint.save()
            except Exception as e:
                print(f"Error updating BlockedUser: {e}")

            try:
                complaints = Complaint.objects.filter(device_identifier=old_fingerprint).all()
                for complaint in complaints:
                    complaint.device_identifier = fingerprint
                    complaint.save()
            except:
                pass


        isBlocked_ip = BlockedUser.objects.filter(ip_address=ip).exists()
        isBlockedFingerprint = BlockedUser.objects.filter(device_identifier=fingerprint).exists()

        try:
            if isBlocked_ip and not isBlockedFingerprint:
                blocked_user = BlockedUser.objects.filter(ip_address=ip).first()
                blocked_user.device_identifier = fingerprint
                blocked_user.save()
            if isBlockedFingerprint and not isBlocked_ip:
                blocked_user = BlockedUser.objects.filter(device_identifier=fingerprint).first()
                blocked_user.ip_address = ip
                blocked_user.save()
        except:
            pass

        if isBlocked_ip or isBlockedFingerprint:
            return JsonResponse({'isBlocked': True})
        else:
            return JsonResponse({'isBlocked': False})