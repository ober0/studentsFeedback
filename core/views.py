import random
import secrets
import re
from django.db.models import Q, F, Value, When, Case
from django.db.models import Count, Subquery, OuterRef, Exists
from django.db.models.functions import Lower, Substr, Concat
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
    """
        Декоратор для проверки, авторизован ли студент.
        Если пользователь не авторизован, перенаправляет на страницу авторизации с сохранением текущего пути.
    """

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if 'email' not in request.session or request.session.get('email') == None:
                return redirect(f'/auth/?next={redirect_url}')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator



def board(request):
    """
        Отображает главную страницу. Учитывает текущие параметры фильтрации и поиска.
        Передает данные авторизации и текущего пользователя в контекст.
    """

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

    return render(request, 'core/board.html', context)





def exit(request):
    """
        Завершает сессию пользователя, удаляя данные из request.session.
        Перенаправляет на главную страницу.
    """

    request.session['student_id'] = None
    request.session['email'] = None
    return redirect('index')


def auth(request):
    """
        Отображает страницу авторизации. Сохраняет путь для перенаправления после авторизации.
    """

    if request.method == 'GET':
        next = request.GET.get('next')
        if not next:
            next = '/'
        return render(request, 'core/auth.html', {'next': next})


def send_code(request):
    """
        Генерирует код подтверждения для входа и отправляет его на указанный email.
        Код сохраняется в Redis с временем жизни 5 минут.
    """

    if request.method == 'POST':
        code = random.randint(100000, 999999)
        next = request.POST.get('next')
        email = request.POST.get('email')
        header = 'Код для входа в аккаунт на сайте ks54'

        send_email.delay(header=header, text=code, email=email)

        r.setex(email, 300, code)

        return render(request, 'core/enter_code.html', {'email': email, 'next': next})

def check_code(request):
    """
        Проверяет код подтверждения, введенный пользователем.
        Если код верен, создает пользователя (если он не существует) и сохраняет его данные в сессии.
    """

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
    """
        Отображает страницу для создания жалобы. Генерирует уникальную ссылку для жалобы.
    """

    user_id = request.session.get('student_id')
    user = Students.objects.filter(id=user_id).first()
    link = secrets.token_hex(32)
    link_url = settings.COMPLAINTS_VIEW_URL + link + '/'

    try:
        email = user.email
    except:
        email = None
    return render(request, 'core/create_complaint.html', {'email': email, 'student_id': user_id,
        'auth': True if user_id else False, 'link': link, 'link_url': link_url})


def blocked(request):
    """
       Отображает страницу с информацией о блокировке пользователя.
   """

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
    """
        Отображает страницу с жалобами текущего пользователя.
    """

    student_id = request.session.get('student_id')
    student = Students.objects.filter(id=int(student_id)).first()

    context = {
        'user_id': student_id,
        'email': student.email
    }

    return render(request, 'core/my_complaints.html', context)

def loadmore(request):
    """
        Загружает дополнительный список жалоб с учетом фильтров поиска и сортировки.
        Возвращает результат в формате JSON.
    """

    if request.method == 'POST':

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
                liked=Exists(likes_subquery),
                admin_name=Case(
                    When(admin__first_name='', then=Value('admin')),
                    default=Concat(
                        F('admin__first_name'),
                        Value(' '),
                        Substr(F('admin__last_name'), 1, 1),
                        Value('.')
                    )
                )
                ).order_by(sort_query)
            complaints_count_all = len(complaints)
            complaints = complaints[start : start + settings.COMPLAINTS_LIST_SIZE]
            # Формирование данных для ответа
            complaints_data = []
            for complaint in complaints:
                link = settings.COMPLAINTS_VIEW_URL + complaint.reply_code + '/'
                complaints_data.append({
                    'id': complaint.id,
                    'is_anonymous': complaint.is_anonymous,
                    'user_name': complaint.user_name if not complaint.is_anonymous else None,
                    'category': complaint.category,
                    'content': complaint.content,
                    'response_text': complaint.response_text or None,
                    'created_at': format_datetime(complaint.created_at, "d MMMM yyyy, HH:mm", locale="ru") if complaint.created_at else None,
                    'liked': complaint.liked,
                    'like_count': complaint.like_count,
                    'admin': complaint.admin_name,
                    'link': link,
                })

            context = {
                'success': True,
                'complaints_count': complaints_count_all,
                'complaints': complaints_data,
                'is_admin': request.user.is_staff,
            }

        except Exception as e:
            context = {'success': False, 'error': str(e)}

        return JsonResponse(context)


def loadmore_my(request):
    """
        Загружает дополнительный список жалоб, принадлежащих текущему пользователю, с учетом поиска.
        Объединяет результаты из разных источников (IP, email, user_id и т.д.).
        Возвращает результат в формате JSON.
    """

    if request.method == 'POST':
        try:
            start = int(request.POST.get('start', 0))
            # Получаем данные пользователя
            student_id = request.session.get('student_id')
            student = Students.objects.filter(id=int(student_id)).first()

            data = request.POST

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            pskey = data.get('pskey')

            if not student:
                return JsonResponse({'success': False, 'error': 'Пользователь не найден'})

            # Обрабатываем параметры поиска
            search_query = request.GET.get('search', '')
            escaped_search_query = re.escape(search_query)


            complaints = Complaint.objects.filter(is_spam=False).filter(
                Q(user=student) | Q(email_for_reply=student.email) | Q(ip_address=ip) | Q(device_identifier=pskey)
            ).filter(
                Q(content__iregex=escaped_search_query) | Q(category__iregex=escaped_search_query)
            ).annotate(
                admin_name=Case(
                    When(admin__first_name='', then=Value('admin')),  # Если имя пустое, подставляем 'admin'
                    default=Concat(
                        F('admin__first_name'),
                        Value(' '),
                        Substr(F('admin__last_name'), 1, 1),
                        Value('.')
                    )
                )
            ).order_by('-created_at')

            complaints_count_all = len(complaints)
            complaints = complaints[start: start + settings.COMPLAINTS_LIST_SIZE]

            # Убираем дубликаты вручную
            unique_complaints = {complaint.id: complaint for complaint in complaints}.values()
            # Преобразуем жалобы в JSON-формат
            complaints_data = []
            for complaint in unique_complaints:
                link = settings.COMPLAINTS_VIEW_URL + complaint.reply_code + '/'
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
                    'admin':complaint.admin_name,
                    'link': link
                })

            return JsonResponse({'success': True, 'complaints_count': complaints_count_all, 'complaints': complaints_data})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'}, status=405)


def index(request):
    student_id = request.session.get('student_id')
    student = Students.objects.filter(id=int(student_id)).first()

    context = {
        'user_id': student_id,
        'email': student.email
    }

    return render(request, 'core/index.html', context)