from __future__ import absolute_import, unicode_literals

# Это гарантирует, что приложение Celery будет загружаться при старте Django.
from .celery import app as celery_app

__all__ = ('celery_app',)
