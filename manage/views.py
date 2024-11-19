from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import BlockedUser, UserUnbanRequest
from complaints.models import Complaint
from django.db.models import Q
from django.contrib import messages

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


def load_banned_complaint(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    fingerprint = request.POST.get('visitorId')

    try:
        blockedUser = BlockedUser.objects.filter(Q(ip_address=ip) | Q(device_identifier=fingerprint)).order_by('-blocked_at').first()
        complaint = blockedUser.complaints_spam_id
    except:
        print(1)
        return JsonResponse({'success': False, 'redirect': '/'})

    return JsonResponse({
        'success': True,
        'id': complaint.id,
        'category': complaint.category,
        'content': complaint.content,
        'reason': blockedUser.block_reason
    })


def unban_request(request):
    if request.method == 'POST':
        data = request.POST

        request_text = data.get('text')
        complaint_id = data.get('complaint_id')
        fingerprint = data.get('device_identifier')

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        complaint = Complaint.objects.filter(id=complaint_id).first()

        try:
            userUnbanRequest = UserUnbanRequest.objects.create(ip_address=ip, device_identifier=fingerprint, complaint=complaint, request_text=request_text)
            userUnbanRequest.save()

            messages.success(request, 'Успешно. В случае одобрения заявки вы будете разблокированы.')
            return redirect('/')
        except:
            messages.error(request, 'Создать заявку не удалось. Попробуйте снова')
            return redirect('/blocked/')