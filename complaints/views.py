from functools import wraps

from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .task import unbanUser
from core.models import Students
from complaints.models import Complaint, ComplaintLike
from manage.models import BlockedUser
import requests
from django.conf import settings
from django.contrib import messages
from core.task import send_email


def staff_or_superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        else:
            return redirect(settings.LOGIN_URL) 
    return _wrapped_view


def create(request):
    if request.method == 'POST':
        data = request.POST

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        pskey = data.get('pskey')

        if not pskey:
            messages.error(request, 'Внутренняя ошибка. Перезагрузите страницу')
            return redirect('/')

        isBlocked_ip = BlockedUser.objects.filter(ip_address=ip).exists()
        isBlockedFingerprint = BlockedUser.objects.filter(device_identifier=pskey).exists()

        if isBlocked_ip or isBlockedFingerprint:
            return redirect('/blocked/')



        time_interval_5 = timezone.now() - timezone.timedelta(minutes=5)

        recent_complaints = Complaint.objects.filter(Q(ip_address=ip) | Q(device_identifier=pskey)).filter(created_at__gte=time_interval_5).order_by('-created_at')
        if len(recent_complaints) >= settings.MAX_COMPLAINTS_COUNT:
            messages.error(request, f'Ваши действия похожи на автоматические, вы заблокированы на {settings.BAN_FOR_SPAM_TIME} мин')

            block_end_time = timezone.now() + timedelta(minutes=settings.BAN_FOR_SPAM_TIME)

            block_user = BlockedUser.objects.create(ip_address=ip, device_identifier=pskey,
                                                    block_reason='Подозрение на спам',
                                                    ended_at=block_end_time,
                                                    complaints_spam_id=recent_complaints[0])
            block_user.save()

            for complaint in recent_complaints:
                complaint.is_spam = True
                complaint.save()

            if block_end_time:
                unbanUser.apply_async(
                    kwargs={'id': block_user.id},
                    eta=block_end_time
                )

            return redirect('/blocked/')


        category = data.get("category")

        anonymous = True if data.get('anonymous') else False
        print(anonymous)
        if anonymous:
            name = None
            group = None
        else:
            name = data.get("name")
            group = data.get("group")


        content = data['text']

        response_method = data['response-method']
        if response_method == 'email':
            email = data['email']
        else:
            email = None

        link = request.POST.get('link')

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
                    if settings.BAN_MATS_TIME != 'forever':
                        block_end_time = timezone.now() + timedelta(hours=settings.BAN_MATS_TIME)
                    else:
                        block_end_time = None
                    block_user = BlockedUser.objects.create(ip_address=ip, device_identifier=pskey,
                                                            block_reason='Автоматическая блокировка',
                                                            complaints_spam_id=complaint,
                                                            ended_at=block_end_time)
                    block_user.save()
                    return redirect('/blocked/')
                except Exception as e:
                    print(str(e))

        except Exception as e:
            messages.error(request, str(e))
            return redirect(f'/complaints/create/')

        messages.success(request, 'Обращение создано')
        return redirect('/')

@staff_or_superuser_required
def delete(request, id):
    if request.method == 'POST':
        try:
            complain = Complaint.objects.filter(id=id).first()
            complain.delete()
            return JsonResponse({'success': True})
        except:
            messages.error(request, 'Ошибка при удалении записи.')
            return JsonResponse({'success': False})

@staff_or_superuser_required
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
        messages.success(request, 'Ответ отправлен')
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
    if complaint:
        context = {'complaint': complaint}
        return render(request, 'core/complaint_view.html', context)
    return redirect('index')


@staff_or_superuser_required
def delete_public(request, id):
    if request.method == 'POST':
        try:
            complaint = Complaint.objects.filter(id=id).first()
            complaint.is_published = False
            complaint.save()
            return JsonResponse({'success': True})
        except:
            messages.error(request, 'Ошибка при удалении записи со стены.')
            return JsonResponse({'success': False})