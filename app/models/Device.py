from .. import db
from flask_sqlalchemy import SQLAlchemy
import datetime


class Device(db.Model):
  __tablename__ = 'device'

  uid = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
  uni_id = db.Column(db.String(255))
  name = db.Column(db.String(255))
  device_type = db.Column(db.String(255))
  cpu = db.Column(db.String(255))
  memory = db.Column(db.String(255))
  os = db.Column(db.String(255))
  data_meta = db.Column(db.String(255))
  register_time = db.Column(db.DateTime)

  def get_dict(self):
    return {
      'uid': self.uid,
      'uni_id': self.uni_id,
      'name': self.name,
      'device_type': self.device_type,
      'cpu': self.cpu,
      'memory': self.memory,
      'os': self.os,
      'data_meta': self.data_meta,
      'register_time': self.register_time.strftime('%Y-%m-%d %H:%M:%S'),
    }
