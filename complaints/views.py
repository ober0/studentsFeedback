import secrets

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from core.models import Students
from complaints.models import Complaint, ComplaintLike
from manage.models import BlockedUser
import requests
from django.conf import settings
from django.contrib import messages
from core.task import send_email

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
            link = request.POST.get('link')
            email = None

        publish = True if data.get('publish') else False

        moderation_request = requests.post(settings.MODERATION_REQUEST_URL, data={
            'text': str(content)
        })
        if moderation_request.status_code != 200:
            messages.error(request, 'Moderation request failed')
            return redirect(f'/complaints/create/')

        response = moderation_request.json()
        print(response)
        level = response.get('level')
        print(level)
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

@login_required(login_url='/admin/login/')
def add_response(request, id):
    if request.method == 'POST':
        is_published = request.POST.get('is_published')
        response_text = request.POST.get('response_text')
        print(is_published)
        try:
            complaint = Complaint.objects.get(id=id)
            complaint.status = 'closed'
            complaint.needs_review = False
            complaint.is_published = (is_published == 'on')
            complaint.response_text = response_text
            complaint.admin = request.user
            complaint.save()

            if complaint.email_for_reply is not None:

                header = f'Ответ на обращение #{complaint.id} на сайте ks54'
                text = f'''Ответ администратора:
{response_text}
Посмотреть обращения можно на {settings.VIEW_COMPLAINTS_URL}
                '''
                send_email.delay(email=complaint.email_for_reply, text=text, header=header)
        except:
            messages.error(request, 'Ошибка.')

        return redirect('/manage/complaint/open/')

def like(request):
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        if student_id:
            cid = request.POST.get('cid')
            try:
                complaint = Complaint.objects.get(id=cid)
                student = Students.objects.get(id=student_id)
                like = ComplaintLike.objects.create(complaint=complaint, user=student)
                like.save()
                return JsonResponse({'success': True})
            except Exception as e:
                messages.error(request, str(e))
                return JsonResponse({'success': False, 'error': str(e)})

        else:
            return JsonResponse({'success': False, 'error': 'NotAuth'})

def unlike(request):
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        if student_id:
            cid = request.POST.get('cid')
            try:
                complaint = Complaint.objects.get(id=cid)
                student = Students.objects.get(id=student_id)
                like = ComplaintLike.objects.filter(user=student, complaint=complaint).first()
                like.delete()
                return JsonResponse({'success': True})
            except Exception as e:
                messages.error(request, str(e))
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            return JsonResponse({'success': False, 'error': 'NotAuth'})


def complaint(request, key):
    complaint = Complaint.objects.filter(reply_code=key).first()
    print(complaint.category)
    if complaint:
        context = {'complaint': complaint}
        return render(request, 'core/complaint_view.html', context)
    return redirect('index')