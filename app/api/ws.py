from app import socketio
from flask_socketio import send, emit
from flask import request, current_app, jsonify
from datetime import datetime
from app.api import redis_func
from app.api import db_func

all_background_thread = set()

def start_task(json, uid):
  sid = redis_func.get_device_wsid(uid)
  if sid:
    socketio.emit('new_task', json, json=True, room=sid)
    return True
  return False

def stop_task(json, uid):
  sid = redis_func.get_device_wsid(uid)
  if sid:
    socketio.emit('stop_task', json, json=True, room=sid)
    return True
  return False

def reboot(uid):
  sid = redis_func.get_device_wsid(uid)
  if sid:
    socketio.emit('reboot', room=sid)
    return True
  return False

def get_model_detail_period(mid, sid, uids):
  while sid in all_background_thread:
    model_info = redis_func.get_model_status(mid)
    device_info = []
    for uid in uids:
      res = redis_func.get_device_status(uid)
      res["times"] = redis_func.get_device_model_contribute_time(uid, mid)
      res["status"] = redis_func.get_device_model_status(uid, mid)

      device_info.append(res)

    ret = {"model_info": model_info, "device_info": device_info}
    socketio.emit('push_task_info',
                  ret,
                  namespace='/dashboard',
                  json=True, room=sid)

    socketio.sleep(5)


@socketio.on('heart')
def heart(json):
  try:
    uid = str(json.get('uid',''))
    if uid == '':
      return 'Access Denied', 404
    sid = request.sid
    ip = request.remote_addr
    ping = json.get('ping','')
    cpu_ing = json.get('cpu_ing','')
    memory_ing = json.get('memory_ing','')
    running = json.get('running','')
    timestamp = int(datetime.now().timestamp())
    redis_func.update_device_status(uid, dict(sid=sid,
                                              ip=ip,
                                              cpu_ing=cpu_ing,
                                              memory_ing=memory_ing,
                                              running=running,
                                              timestamp=timestamp,
                                              ping=ping))

  except Exception as e:
    current_app.logger.error(e)

@socketio.on('task_states_update')
def task_states_update(json):
  try:
    uid = str(json.get('uid',''))
    mid = str(json.get('mid',''))
    status = str(json.get('status',''))
    if uid == '' or mid == '' or status == '':
      return 'Access Denied', 404

    redis_func.update_device_model_status(uid, mid, status)

  except Exception as e:
    current_app.logger.error(e)

# @socketio.on('get_device_info')
# def heart(json):
#   try:
#     page = 1
#     if request.json:
#       page = request.json.get('page', 1)
#
#     query_result, count = db_func.query_device({}, page=page)
#
#     for d in query_result:
#       res = redis_func.get_device_status(d["uid"])
#       d.update(res)
#       d["show"] = False
#
#     return jsonify({"result": 0, "message": "success", "value": query_result, "count": count})
#
#   except Exception as e:
#     current_app.logger.error(e)
#     return jsonify({"result": -2, "message": "failed"})


@socketio.on('apply_model_info', namespace='/dashboard')
def apply_model_info(json):
  # print(request.sid)
  # print('received json: ' + str(json))
  all_background_thread.add(request.sid)
  socketio.start_background_task(get_model_detail_period, json['mid'], request.sid, json["uids"])

@socketio.on('disconnect', namespace='/dashboard')
def disconnect():
  print(request.sid, ' disconnect')
  all_background_thread.remove(request.sid)

@socketio.on('my event')
def handle_my_custom_event(json):
  print(request.sid)
  print('received json: ' + str(json))
