import datetime

from sqlalchemy import text
import pypinyin
from ..models import Device, Task
from flask import jsonify, current_app, session
from .. import db, app
from werkzeug.security import generate_password_hash, check_password_hash
import xlrd
import traceback


def add_device(info):
    device = Device(**info)
    db.session.add(device)
    db.session.commit()

    dic = device.get_dict()
    return dic["uid"], dic["register_time"]

def query_device(data, order_by='', page=1):
  option = data
  try:
    qs_result = Device.query.filter_by(**option).order_by(text(order_by)).paginate(page=page, per_page=10,
                                                                                      error_out=False)
    qs_count = Device.query.filter_by(**option).count()
    q_result = qs_result.items
  except Exception as e:
    traceback.print_exc()
    current_app.logger.error(e)
    return [], 0

  query_result = list()
  for que_result in q_result:
    query_result.append(que_result.get_dict())

  return query_result, qs_count

def query_device_list(uids):
  try:
    qs_result = Device.query.filter(Device.uid.in_(uids)).all()
    query_result = list()
    for que_result in qs_result:
      query_result.append(que_result.get_dict())
    return query_result
  except Exception as e:
    traceback.print_exc()
    current_app.logger.error(e)
    return []

def delete_device(uid):
  device = Device.query.filter_by(uid=uid).first()
  db.session.delete(device)
  db.session.commit()

def add_task(info):
  task = Task(**info)
  db.session.add(task)
  db.session.commit()

  return task.get_dict()["mid"]

def query_task(data, order_by='', page=1):
  option = data
  try:
    qs_result = Task.query.filter_by(**option).order_by(text(order_by)).paginate(page=page, per_page=10,
                                                                                   error_out=False)
    qs_count = Task.query.filter_by(**option).count()
    q_result = qs_result.items
  except Exception as e:
    traceback.print_exc()
    current_app.logger.error(e)
    return [], 0

  query_result = list()
  for que_result in q_result:
    query_result.append(que_result.get_dict())

  return query_result, qs_count


def delete_task(mid):
  task = Task.query.filter_by(mid=mid).first()
  db.session.delete(task)
  db.session.commit()
