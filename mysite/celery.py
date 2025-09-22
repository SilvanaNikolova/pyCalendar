import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

celery_app = Celery('mysite')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()
# Опит за задаване на часова зона за изпълнение на задачите в локално време
celery_app.enable_utc = False
celery_app.conf.timezone = 'Europe/Sofia'