import random

from django.db.models import Count, Subquery, OuterRef, Exists
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from complaints.models import Complaint, ComplaintLike
from .models import Students
from .redis import r
from .task import send_email



def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'student_mail' not in request.session:
            return JsonResponse({'auth': False})
        return view_func(request, *args, **kwargs)
    return wrapper

# messages.success(request, 'Вы успешно вошли!')



def index(request):
    student_id = request.session.get('student_id')
    email = request.session.get('email')

    likes_subquery = ComplaintLike.objects.filter(
        complaint=OuterRef('pk'),
        user=student_id
    )

    complaints = Complaint.objects.filter(is_published=True).annotate(
        like_count=Count('complaintlike'),
        liked=Exists(likes_subquery)
    )

    context = {
        'complaints': complaints,
        'email': email,
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
        return render(request, 'core/auth.html')


def send_code(request):
    if request.method == 'POST':
        code = random.randint(100000, 999999)
        email = request.POST.get('email')
        header = 'Код для входа в аккаунт на сайте ks54'

        send_email.delay(header=header, text=code, email=email)

        r.setex(email, 300, code)

        return render(request, 'core/enter_code.html', {'email': email})

def check_code(request):
    if request.method == 'POST':
        code_input = request.POST.get('code')
        email = request.POST.get('email')
        code = r.get(email).decode('utf-8')

        print(code)
        print(code_input)
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

            return redirect('index')

        else:
            messages.error(request, 'Код неверный!')
            return render(request, 'core/enter_code.html', {'email': email})


def create_complaint(request):
    email, user_id = request.session.get('email'), request.session.get('student_id')

    return render(request, 'core/create_complaint.html', {'email': email, 'user_id': user_id})


def blocked(request):
    return JsonResponse({'data': 'Вы заблокированы'})