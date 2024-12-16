from app.models import Task, db
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class TaskService:
    @staticmethod
    def initialize_database():
        try:
            db.create_all()
            TaskService.cleanup_completed_tasks()
            logger.info('Database initialized and cleaned up successfully')
        except SQLAlchemyError as e:
            logger.error(f'Error initializing database: {str(e)}')
            db.session.rollback()
            raise

    @staticmethod
    def add_task(task_type, params):
        try:
            task = Task(task_type=task_type, params=params, status='pending')
            db.session.add(task)
            db.session.commit()
            logger.info(f'Task added successfully: {task.id}')
            return task
        except SQLAlchemyError as e:
            logger.error(f'Error adding task: {str(e)}')
            db.session.rollback()
            raise

    @staticmethod
    def get_all_tasks():
        try:
            return Task.query.order_by(Task.id.desc()).all()
        finally:
            db.session.close()

    @staticmethod
    def get_next_pending_task():
        try:
            return Task.query.filter_by(status='pending').order_by(Task.created_at).first()
        finally:
            db.session.close()

    @staticmethod
    def update_task_status(task_id, status, result=None, reason=None):
        try:
            task = Task.query.get(task_id)
            if task:
                task.status = status
                task.result = result
                task.reason = reason
                db.session.commit()
                logger.info(f'Task {task_id} updated with status: {status}')
            else:
                logger.error(f'Task {task_id} not found')
        except SQLAlchemyError as e:
            logger.error(f'Error updating task: {str(e)}')
            db.session.rollback()
            raise
        finally:
            db.session.close()

    @staticmethod
    def cleanup_completed_tasks():
        try:
            Task.query.filter(Task.status != 'pending').delete()
            db.session.commit()
            logger.info("Non-pending tasks cleaned up successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error during task cleanup: {str(e)}")
            db.session.rollback()
            raise
