from .worker import celery_app
@celery_app.task
def nightly_job():
    return {"ok": True}
