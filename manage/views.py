from datetime import timedelta
from functools import wraps

import requests
from django.utils.http import urlencode

from complaints.task import unbanUser
from babel.dates import format_datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import BlockedUser, UserUnbanRequest
from complaints.models import Complaint
from django.db.models import Q, F, OuterRef, Subquery
from django.contrib import messages


def getAdminName(request):
    """
        Получает имя администратора для отображения в интерфейсе.
        Если имя или фамилия отсутствуют, возвращает 'admin'.
    """

    first_name = request.user.first_name
    if first_name is None or first_name == '':
        return 'admin'
    try:
        second_name = request.user.last_name[0]
    except IndexError:
        second_name = ''

    return first_name + ' ' + second_name + '.'


def staff_or_superuser_required(view_func):
    """
        Декоратор для проверки, что пользователь является либо staff, либо superuser.
        Если пользователь не аутентифицирован, перенаправляет на страницу входа с сохранением пути.
        Если пользователь не имеет прав, перенаправляет на главную страницу.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        else:
            if not request.user.is_authenticated:
                next_url = request.get_full_path()  # Получаем текущий путь
                login_url_with_next = f"{settings.LOGIN_URL}?{urlencode({'next': next_url})}"
                return HttpResponseRedirect(login_url_with_next)

            # Если пользователь не имеет доступа (не staff и не superuser)
            return redirect('')

    return _wrapped_view

@csrf_exempt
def check_fingerprint(request):
    """
        Проверяет, заблокирован ли пользователь по IP-адресу или устройству (fingerprint).
        Если старый fingerprint изменился, обновляет его в базе.
    """

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
    """
        Загружает информацию о заблокированной жалобе для текущего пользователя.
        Если блокировка истекла, удаляет запись и перенаправляет пользователя.
    """

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
        return JsonResponse({'success': False, 'redirect': '/'})

    end = blockedUser.ended_at

    if end:
        if end < timezone.now():
            blockedUser.delete()
            return JsonResponse({'success': False, 'redirect': '/complaints/create/'})

        end = format_datetime(timezone.localtime(end), "d MMMM HH:mm:ss", locale="ru")
    else:
        end = 'Никогда'
    context = {
        'success': True,
        'id': complaint.id,
        'category': complaint.category,
        'content': complaint.content,
        'reason': blockedUser.block_reason,
        'end': end
    }
    request = UserUnbanRequest.objects.filter(complaint=complaint).filter(Q(review_result='rejected') | Q(review_result='in_work')).first()
    if request:
        context['isRequestSend'] = True
        context['status'] = 'В работе' if request.review_result == 'in_work' else 'Закрыто'
        return JsonResponse(context)

    context['isRequestSend'] = False
    return JsonResponse(context)


def unban_request_create(request):
    """
       Создает заявку на разблокировку пользователя.
       Выполняет проверку текста заявки через сервис модерации.
   """

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


        moderation_request = requests.post(settings.MODERATION_REQUEST_URL, data={
            'text': str(request_text),
        })
        if moderation_request.status_code != 200:
            messages.error(request, 'Moderation request failed')
            return redirect(f'/blocked/')

        response = moderation_request.json()
        level = response.get('level')

        if level == 1:
            messages.error(request, 'Не используйте нецензурную лексику!')
            return redirect(f'/blocked/')
        if level == 2:
            messages.error(request, 'Нецензурная лексика запрещена, блокировка продлена.')
            blocked_user = BlockedUser.objects.filter(Q(device_identifier=fingerprint) | Q(ip_address=ip)).first()
            blocked_user.ended_at = None
            blocked_user.save()
            return redirect(f'/blocked/')


        complaint = Complaint.objects.filter(id=complaint_id).first()

        try:
            userUnbanRequest = UserUnbanRequest.objects.create(ip_address=ip, device_identifier=fingerprint, complaint=complaint, request_text=request_text)
            userUnbanRequest.save()

            messages.success(request, 'Успешно. В случае одобрения заявки вы будете разблокированы.')
            return redirect('/')
        except Exception as e:
            print(str(e))
            messages.error(request, 'Создать заявку не удалось. Попробуйте снова')
            return redirect('/blocked/')


@staff_or_superuser_required
def open_complaints(request):
    """
        Отображает список открытых жалоб для администраторов.
        Фильтрует по категории, если указана.
    """

    page = 'Открытые обращения'
    category = request.GET.get('category')

    name = getAdminName(request)

    category = request.GET.get('category')
    filters = {
        'status': 'open',
        'is_spam': False,
        'needs_review': False
    }

    if category:
        filters['category'] = category

    complaints = Complaint.objects.filter(**filters).order_by('-created_at')

    context = {
        'complaints': complaints,
        'name': name,
        'page': page,
        'category': category
    }
    return render(request, 'manage/complaints_list.html', context)


@staff_or_superuser_required
def open_need_review_complaints(request):
    """
        Отображает список жалоб, которые требуют модерации.
    """

    page = 'Спам'
    category = request.GET.get('category')

    name = getAdminName(request)

    category = request.GET.get('category')
    filters = {
        'status': 'open',
        'is_spam': False,
        'needs_review': True
    }

    if category:
        filters['category'] = category

    complaints = Complaint.objects.filter(**filters).order_by('-created_at')

    context = {
        'complaints': complaints,
        'name': name,
        'page': page,
        'category': category
    }
    return render(request, 'manage/complaints_list.html', context)


@staff_or_superuser_required
def close_complaints(request):
    """
        Отображает список закрытых жалоб.
    """

    page = 'Закрытые обращения'
    category = request.GET.get('category')

    name = getAdminName(request)


    category = request.GET.get('category')
    filters = {
        'status': 'closed',
        'is_spam': False,
    }

    if category:
        filters['category'] = category

    complaints = Complaint.objects.filter(**filters).order_by('-created_at')

    context = {
        'complaints': complaints,
        'name': name,
        'page': page,
        'category': category
    }
    return render(request, 'manage/complaints_list.html', context)


@staff_or_superuser_required
def complaint(request, id):
    """
        Отображает информацию о конкретной жалобе.
        Разные шаблоны используются для открытых и закрытых жалоб.
    """

    complaint = Complaint.objects.get(id=id)

    name = getAdminName(request)

    context = {
        'complaint': complaint,
        'name': name
    }

    if complaint.status == 'open':
        return render(request, 'manage/complaint_open.html', context)
    else:
        return render(request, 'manage/complaint_close.html', context)


@staff_or_superuser_required
def ban(request, id):
    """
        Блокирует пользователя, связанного с указанной жалобой.
        Может задать срок блокировки или оставить её бессрочной.
    """

    if request.method == 'POST':
        reason = request.POST.get('reason')
        time = request.POST.get('time')
        print(time)

        if not reason:
            reason = 'Заблокирован администратором'

        try:
            complaint = Complaint.objects.get(id=id)

            ip = complaint.ip_address
            fingerprint = complaint.device_identifier

            complaint.is_spam = True
            complaint.status = 'closed'
            complaint.save()

            if time != 'forever' and time:
                block_end_time = timezone.now() + timedelta(hours=int(time))
                print(block_end_time)
            else:
                block_end_time = None

            block_user = BlockedUser.objects.create(ip_address=ip, device_identifier=fingerprint, block_reason=reason, complaints_spam_id=complaint, ended_at=block_end_time)
            block_user.save()

            if time != 'forever':
                unbanUser.apply_async(
                    kwargs={'id': block_user.id},
                    eta=block_end_time
                )

            messages.success(request, 'Пользователь заблокирован!')
            return JsonResponse({'success': True})

        except Exception as e:
            messages.error(request, f'Ошибка! {str(e)}')
            return JsonResponse({'success': False})


@staff_or_superuser_required
def index(request):
    """
        Перенаправляет на список открытых жалоб.
    """

    return redirect('open_complaints')


@staff_or_superuser_required
def unban_requests_check(request):
    """
        Отображает список заявок на разблокировку, которые находятся в обработке.
    """

    blocked_reason_subquery = BlockedUser.objects.filter(
        complaints_spam_id=OuterRef('complaint')
    ).values('block_reason')[:1]

    # Основной запрос с аннотациями
    unban_requests = UserUnbanRequest.objects.filter(review_result='in_work').annotate(
        is_anonymous=F('complaint__is_anonymous'),
        user_name=F('complaint__user_name'),
        block_reason=Subquery(blocked_reason_subquery)
    )

    name = getAdminName(request)

    context = {
        'requests': unban_requests,
        'name': name
    }

    return render(request, 'manage/unban_requests_list.html', context)


def unban_request_check(request, id):
    """
        Отображает подробности конкретной заявки на разблокировку.
    """

    unban_request = UserUnbanRequest.objects.filter(id=id).annotate(
        name=F('complaint__user_name'),
        is_anonymous=F('complaint__is_anonymous'),
        category=F('complaint__category'),
        text=F('complaint__content'),
        reason=Subquery(
            BlockedUser.objects.filter(complaints_spam_id=OuterRef('complaint')).values('block_reason')[:1]
        ),
        ended_at=Subquery(BlockedUser.objects.filter(complaints_spam_id=OuterRef('complaint')).values('ended_at')[:1])
    ).first()

    name = getAdminName(request)

    if unban_request:
        context = {
            'unban_request': unban_request,
            'name': name
        }

        return render(request, 'manage/unban_request.html', context)

    else:
        messages.error(request, 'Запрос не найден')
        return redirect('unban_requests')


def unban_requests_close(request, id):
    """
        Отклоняет заявку на разблокировку.
    """

    user_unban_request = get_object_or_404(UserUnbanRequest, id=id)
    try:
        user_unban_request.review_result = 'rejected'
        user_unban_request.reviewed_by = request.user
        user_unban_request.save()
        messages.success(request, 'Заявка отклонена')
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')

    return redirect('unban_requests')


def unban_requests_approve(request, id):
    """
       Одобряет заявку на разблокировку и удаляет запись о блокировке.
   """

    user_unban_request = get_object_or_404(UserUnbanRequest, id=id)

    blocked_user = BlockedUser.objects.filter(complaints_spam_id=user_unban_request.complaint).first()

    if blocked_user:
        try:
            blocked_user.delete()
            user_unban_request.review_result = 'unbanned'
            user_unban_request.reviewed_by = request.user
            user_unban_request.save()
            messages.success(request, 'Пользователь разблокирован')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
    else:
        messages.error(request, f'Ошибка: Пользователь не найден')

    return redirect('unban_requests')
