import secrets
from django.http import JsonResponse
from django.shortcuts import render, redirect
from manage.models import BlockedUser

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

        text = data['text']

        response_method = data['response-method']
        if response_method == 'email':
            email = data['email']
            link = None
        else:
            link = secrets.token_hex(24)
            email = None

        publish = True if data.get('publish') else False




        return JsonResponse({})