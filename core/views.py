import random
import secrets
import re
from django.db.models import Q
from django.db.models import Count, Subquery, OuterRef, Exists
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from complaints.models import Complaint, ComplaintLike
from .models import Students
from .redis import r
from .task import send_email
from django.conf import settings
from babel.dates import format_datetime



def student_required(redirect_url):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if 'email' not in request.session or request.session.get('email') == None:
                return redirect(f'/auth/?next={redirect_url}')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# messages.success(request, 'Вы успешно вошли!')

def index(request):
    # likes or time
    sort = request.GET.get('filter')
    if sort == 'time':
        sort_query = '-created_at'
    elif sort == 'likes':
        sort_query = '-like_count'
    else:
        sort = 'time'
        sort_query = '-created_at'

    search_query = request.GET.get('search', '')

    student_id = request.session.get('student_id')
    email = request.session.get('email')


    context = {
        'email': email,
        'search': search_query,
        'filter': sort,
        'student_id': student_id,
        'auth': True if student_id else False
    }

    return render(request, 'core/index.html', context)





def exit(request):
    request.session['student_id'] = None
    request.session['email'] = None
    return redirect('index')


def auth(request):
    if request.method == 'GET':
        next = request.GET.get('next')
        if not next:
            next = '/'
        return render(request, 'core/auth.html', {'next': next})


def send_code(request):
    if request.method == 'POST':
        code = random.randint(100000, 999999)
        next = request.POST.get('next')
        email = request.POST.get('email')
        header = 'Код для входа в аккаунт на сайте ks54'

        send_email.delay(header=header, text=code, email=email)

        r.setex(email, 300, code)

        return render(request, 'core/enter_code.html', {'email': email, 'next': next})

def check_code(request):
    if request.method == 'POST':
        next = request.POST.get('next')

        code_input = request.POST.get('code')
        email = request.POST.get('email')
        code = r.get(email).decode('utf-8')

        if code == code_input:
            try:
                student = Students.objects.filter(email=email).first()
                id = student.id
            except:
                student = Students.objects.create(email=email)
                student.save()
                id = student.id

            request.session['student_id'] = id
            request.session['email'] = email

            return redirect(str(next))

        else:
            messages.error(request, 'Код неверный!')
            return render(request, 'core/enter_code.html', {'email': email})


def create_complaint(request):
    user_id = request.session.get('student_id')
    user = Students.objects.filter(id=user_id).first()
    link = secrets.token_hex(32)
    link_url = settings.COMPLAINTS_VIEW_URL + link + '/'

    try:
        email = user.email
    except:
        email = None
    return render(request, 'core/create_complaint.html', {'email': email, 'student_id': user_id,
        'auth': True if user_id else False, 'link': link_url})


def blocked(request):
    student_id = request.session.get('student_id')
    email = request.session.get('email')
    context = {
        'student_id': student_id,
        'auth': True if student_id else False,
        'email': email,
    }
    return render(request, 'core/blocked.html', context)

    
@student_required('/complaints/my/')
def my_complaints(request):
    student_id = request.session.get('student_id')
    student = Students.objects.filter(id=int(student_id)).first()


    context = {
        'user_id': student_id,
        'email': student.email
    }

    return render(request, 'core/my_complaints.html', context)

def loadmore(request):
    if request.method == 'POST':
        complaints_count = 3

        start = int(request.POST.get('start', 0))
        student_id = request.session.get('student_id', None)
        email = request.session.get('email', None)


        sort = request.GET.get('filter', 'time')
        if sort == 'time':
            sort_query = '-created_at'
        elif sort == 'likes':
            sort_query = '-like_count'
        else:
            sort_query = '-created_at'


        search_query = request.GET.get('search', '')
        escaped_search_query = re.escape(search_query)

        try:
            # Подзапрос для проверки лайков текущего пользователя
            likes_subquery = ComplaintLike.objects.filter(
                complaint=OuterRef('pk'),
                user=student_id
            )

            # Запрос на получение жалоб
            complaints = Complaint.objects.filter(
                is_published=True,
                is_spam=False,
                needs_review=False
            ).filter(
                Q(content__iregex=escaped_search_query) | Q(category__iregex=escaped_search_query)
            ).annotate(
                like_count=Count('complaintlike'),
                liked=Exists(likes_subquery)
            ).order_by(sort_query)[start : start + complaints_count ]
            print(start, start + complaints_count)
            # Формирование данных для ответа
            complaints_data = []
            for complaint in complaints:
                complaints_data.append({
                    'id': complaint.id,
                    'is_anonymous': complaint.is_anonymous,
                    'user_name': complaint.user_name if not complaint.is_anonymous else None,
                    'category': complaint.category,
                    'content': complaint.content,
                    'response_text': complaint.response_text or None,
                    'created_at': format_datetime(complaint.created_at, "d MMMM yyyy, HH:mm", locale="ru") if complaint.created_at else None,
                    'liked': complaint.liked,
                    'like_count': complaint.like_count
                })

            context = {
                'success': True,
                'complaints_count': len(complaints_data),
                'complaints': complaints_data
            }

        except Exception as e:
            context = {'success': False, 'error': str(e)}

        return JsonResponse(context)


def loadmore_my(request):
    if request.method == 'POST':
        try:
            start = int(request.POST.get('start', 0))
            # Получаем данные пользователя
            student_id = request.session.get('student_id')
            student = Students.objects.filter(id=int(student_id)).first()

            if not student:
                return JsonResponse({'success': False, 'error': 'Пользователь не найден'})

            # Обрабатываем параметры поиска
            search_query = request.GET.get('search', '')
            escaped_search_query = re.escape(search_query)

            # Получаем жалобы
            complaints1 = Complaint.objects.filter(user=student, is_spam=False).filter(
                Q(content__iregex=escaped_search_query) | Q(category__iregex=escaped_search_query)
            ).distinct()

            complaints2 = Complaint.objects.filter(email_for_reply=student.email, is_spam=False).filter(
                Q(content__iregex=escaped_search_query) | Q(category__iregex=escaped_search_query)
            ).distinct()

            # Объединяем запросы без вызова distinct()
            complaints = list(complaints1.union(complaints2).order_by('-created_at'))[start:start+3]

            # Убираем дубликаты вручную
            unique_complaints = {complaint.id: complaint for complaint in complaints}.values()

            # Преобразуем жалобы в JSON-формат
            complaints_data = []
            for complaint in unique_complaints:
                complaints_data.append({
                    'id': complaint.id,
                    'is_anonymous': complaint.is_anonymous,
                    'user_name': complaint.user_name if not complaint.is_anonymous else None,
                    'category': complaint.category,
                    'content': complaint.content,
                    'response_text': complaint.response_text or None,
                    'created_at': format_datetime(
                        complaint.created_at, "d MMMM yyyy, HH:mm", locale="ru"
                    ) if complaint.created_at else None,
                    'is_published': complaint.is_published,
                    'is_public': complaint.is_public,
                })

            return JsonResponse({'success': True, 'complaints': complaints_data})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'}, status=405)
