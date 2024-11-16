from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import render



# @user_passes_test(lambda u: u.is_superuser, login_url='/admin/login/')