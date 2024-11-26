from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import BlockedUser, UserUnbanRequest
from complaints.models import Complaint
from django.db.models import Q
from django.contrib import messages


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

    context = {
        'success': True,
        'id': complaint.id,
        'category': complaint.category,
        'content': complaint.content,
        'reason': blockedUser.block_reason,
    }
    request = UserUnbanRequest.objects.filter(complaint=complaint).filter(Q(review_result='rejected') | Q(review_result='in_work')).first()
    if request:
        context['isRequestSend'] = True
        context['status'] = 'В работе' if request.review_result == 'in_work' else 'Закрыто'
        return JsonResponse(context)

    context['isRequestSend'] = False
    return JsonResponse(context)


def unban_request_create(request):
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
        except Exception as e:
            print(str(e))
            messages.error(request, 'Создать заявку не удалось. Попробуйте снова')
            return redirect('/blocked/')

@login_required(login_url=settings.LOGIN_URL)
def open_complaints(request):
    page = 'Открытые обращения'
    category = request.GET.get('category')

    name = request.user.first_name + ' ' + request.user.last_name[0] + '.'

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


@login_required(login_url=settings.LOGIN_URL)
def open_need_review_complaints(request):
    page = 'Спам'
    category = request.GET.get('category')

    name = request.user.first_name + ' ' + request.user.last_name[0] + '.'

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


@login_required(login_url=settings.LOGIN_URL)
def close_complaints(request):
    page = 'Закрытые'
    category = request.GET.get('category')

    name = request.user.first_name + ' ' + request.user.last_name[0] + '.'


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


@login_required(login_url=settings.LOGIN_URL)
def complaint(request, id):
    complaint = Complaint.objects.get(id=id)
    name = request.user.first_name + ' ' + request.user.last_name[0] + '.'
    context = {
        'complaint': complaint,
        'name': name
    }

    if complaint.status == 'open':

        user_name = request.user.first_name + ' ' + request.user.last_name[0] + '.'
        if not user_name:
            user_name = 'admin'
        return render(request, 'manage/complaint_open.html', context)
    else:
        return render(request, 'manage/complaint_close.html', context)
@login_required(login_url=settings.LOGIN_URL)
def ban(request, id):
    if request.method == 'POST':
        reason = request.POST.get('reason')
        if not reason:
            reason = 'Заблокирован администратором'

        try:
            complaint = Complaint.objects.get(id=id)

            ip = complaint.ip_address
            fingerprint = complaint.device_identifier

            complaint.is_spam = True
            complaint.status = 'closed'
            complaint.save()

            block_user = BlockedUser.objects.create(ip_address=ip, device_identifier=fingerprint, block_reason=reason, complaints_spam_id=complaint)
            block_user.save()
            return JsonResponse({'success':True})

        except Exception as e:
            messages.error(request, f'Ошибка! {str(e)}')
            return JsonResponse({'success': False})

@login_required(login_url=settings.LOGIN_URL)
def index(request):
    return redirect('open_complaints')

@login_required(login_url=settings.LOGIN_URL)
def unban_requests_check(request):
    unban_requests = UserUnbanRequest.objects.all()

    name = request.user.first_name + ' ' + request.user.last_name[0] + '.'

    context = {
        'requests': unban_requests,
        'name': name
    }

    return render(request, 'manage/unban_requests_list.html', context)


def unban_request_check(request, id):
    return JsonResponse({'id': id})