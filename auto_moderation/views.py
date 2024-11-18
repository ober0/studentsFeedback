import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def auto_check(request):
    data = request.POST

    banned_words = []

    path = os.path.join(settings.BASE_DIR / 'auto_moderation', 'static/auto_moderation/ban_words.txt')

    with open(path, 'r', encoding='utf-8') as f:
        banned_words = f.read().splitlines()

    text = str(data['text']).split(' ')
    bad_words_count = 0

    for word in text:
        if word in banned_words:
            bad_words_count += 1

    words = len(text)

    percent = (bad_words_count / words * 100) if words > 0 else 0

    if percent > 0 and percent < 15:
        return JsonResponse({'level':1})
    elif percent >= 15:
        return JsonResponse({'level': 2})
    else:
        return JsonResponse({'level': 0})

