from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем настройку для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studentsFeedback.settings')

# Создаем экземпляр Celery
app = Celery('studentsFeedback')

# Используем строку конфигурации для Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим все задачи в приложениях Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
