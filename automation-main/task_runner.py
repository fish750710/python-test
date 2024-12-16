import time
from app import create_app, db
from app.services.task_service import TaskService
from app.services.task_executor import execute_task
import logging

app = create_app()

logger = logging.getLogger(__name__)

def run_tasks():
    with app.app_context():
        while True:
            task = TaskService.get_next_pending_task()
            if task:
                logger.info(f"Starting to execute task: {task.id}")
                execute_task(app, task)
                logger.info(f"Finished executing task: {task.id}")
            else:
                logger.debug("No pending tasks, waiting...")
                time.sleep(5)  # 如果没有待处理的任务，等待5秒再检查

if __name__ == "__main__":
    run_tasks()