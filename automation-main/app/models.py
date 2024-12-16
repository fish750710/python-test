from app import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.String(50), nullable=False)
    params = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    result = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'params': self.params,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'result': self.result
        }
    @classmethod
    def get_next_pending_task(cls):
        return cls.query.filter_by(status='pending').order_by(cls.created_at).first()
