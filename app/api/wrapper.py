from functools import wraps

from flask import redirect, session, jsonify
from .. import app


def checklogin(func):
  @wraps(func)
  def inner_dashboard(*args, **kwargs):

    if app.config['FLASK_ENV'] == 'development':
      return func(*args, **kwargs)
    if session.get('uid') is None or session.get('role') is None:
      return jsonify({"code": 401, "message": 'Unauthorized'})
    if session.get('role') != 'admin':
      return jsonify({"code": 401, "message": 'Unauthorized'})
    return func(*args, **kwargs)

  return inner_dashboard
