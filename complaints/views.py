import secrets

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from core.models import Students
from complaints.models import Complaint
from manage.models import BlockedUser
import requests
from django.conf import settings
from django.contrib import messages


# Create your views here.
def create(request):
    print(1)
    if request.method == 'POST':
        data = request.POST

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        print(ip)
        pskey = data.get('pskey')

        if not pskey:
            return redirect('/')



        isBlocked_ip = BlockedUser.objects.filter(ip_address=ip).exists()
        isBlockedFingerprint = BlockedUser.objects.filter(device_identifier=pskey).exists()

        if isBlocked_ip or isBlockedFingerprint:
            return redirect('/blocked/')



        category = data.get("category")

        anonymous = True if data.get('anonymous') else False
        if anonymous:
            name = data.get("name")
            group = data.get("group")
        else:
            name = None
            group = None

        content = data['text']

        response_method = data['response-method']
        if response_method == 'email':
            email = data['email']
            link = None
        else:
            link = secrets.token_hex(24)
            email = None

        publish = True if data.get('publish') else False

        moderation_request = requests.post(settings.MODERATION_REQUEST_URL, data={
            'text': str(content)
        })
        if moderation_request.status_code != 200:
            messages.error(request, 'Moderation request failed')
            return redirect(f'/complaints/create/')

        response = moderation_request.json()
        level = response.get('level')

        is_spam = False
        needs_review = False

        if level == 1:
            is_spam = False
            needs_review = True
        elif level == 2:
            is_spam = True
            needs_review = False



        user_id = request.session.get('student_id')

        try:
            user = Students.objects.filter(id=int(user_id)).first()
        except:
            user = None

        try:
            complaint = Complaint.objects.create(user=user,
                                                 content=content,
                                                 category=category,
                                                 user_name=name,
                                                 user_group=group,
                                                 is_anonymous=anonymous,
                                                 email_for_reply=email,
                                                 reply_code=link,
                                                 is_public=publish,
                                                 is_spam=is_spam,
                                                 needs_review=needs_review,
                                                 ip_address=ip,
                                                 device_identifier=pskey
                                                 )
            complaint.save()

            if level == 2:
                try:
                    block_user = BlockedUser.objects.create(ip_address=ip, device_identifier=pskey,
                                                            block_reason='Автоматическая блокировка',
                                                            complaints_spam_id=complaint)
                    block_user.save()
                    return redirect('/blocked/')
                except Exception as e:
                    print(str(e))

        except Exception as e:
            messages.error(request, str(e))
            return redirect(f'/complaints/create/')

        messages.success(request, 'Обращение создано')
        return redirect('/')

@login_required(login_url='/admin/login/')
def delete(request, id):
    if request.method == 'POST':
        try:
            complain = Complaint.objects.filter(id=id).first()
            complain.delete()
            complain.save()
            return JsonResponse({'success': True})
        except:
            messages.error(request, 'Ошибка при удалении записи.')
            return JsonResponse({'success': False})


def add_response(request):
    if request.method == 'POST':
        return JsonResponse({})