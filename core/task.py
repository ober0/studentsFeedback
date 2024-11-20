from django.core.mail import send_mail
from celery import shared_task
from django.conf import settings


@shared_task
def send_email(email, text, header):
    subject = header
    message = text
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(subject=str(subject), html_message=str(message), from_email=from_email, recipient_list=recipient_list)
        return {'success': True}
    except Exception as e:
        return {'success': f'{subject} {message} {from_email} {recipient_list}'}