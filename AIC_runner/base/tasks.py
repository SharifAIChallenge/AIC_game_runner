from celery import shared_task
from .models import Submit


@shared_task(bind=True, queue='compile_queue')
def compile_code(self, submit_id):
    print("Compiling %d" % submit_id)

