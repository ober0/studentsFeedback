from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'student_mail' not in request.session:
            return JsonResponse({'auth': False})
        return view_func(request, *args, **kwargs)
    return wrapper

# messages.success(request, 'Вы успешно вошли!')


