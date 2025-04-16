import os
from celery_app import celery_app
from app.feature_extraction import process_files

@celery_app.task(bind=True)
def process_urls_task(self, whitelist_path: str, blacklist_path: str) -> dict:
    task_id = self.request.id
    try:
        csv_path = process_files(whitelist_path, blacklist_path, task_id)
        return {"status": "SUCCESS", "csv_path": csv_path}
    except Exception as e:
        return {"status": "FAILURE", "error": str(e)}
