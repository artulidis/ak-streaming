from celery import Celery, shared_task
import environ

app = Celery('tasks', broker='redis://redis:6379/0')

@shared_task
def add(x, y):
    return x + y