from celery import Celery
import os
celery_app = Celery(
    "appzero",
    broker=os.getenv("REDIS_URL","redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL","redis://redis:6379/0"),
)
@celery_app.task
def ping():
    return "pong"
