from .. import db
from flask_sqlalchemy import SQLAlchemy
import datetime


class Task(db.Model):
  __tablename__ = 'task'

  mid = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
  name = db.Column(db.String(255))
  model_type = db.Column(db.String(255))
  model_path = db.Column(db.Text)  # 开始训练后填写
  program_info = db.Column(db.JSON)
  devices = db.Column(db.Text)
  status = db.Column(db.String(255), default="正在训练")
  create_time = db.Column(db.DateTime, default=datetime.datetime.now)
  end_time = db.Column(db.DateTime)


  def get_dict(self):
    return {
      'mid': self.mid,
      'name': self.name,
      'model_type': self.model_type,
      'model_path': self.model_path,
      'program_info': self.program_info,
      'devices': self.devices,
      'status': self.status,
      'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else ''
    }
