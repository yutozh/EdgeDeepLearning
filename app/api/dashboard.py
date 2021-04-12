"""
Routing for vote
"""

from datetime import datetime
from flask import request, session, jsonify, abort, current_app
from flask_restplus import Resource
from app.api.wrapper import checklogin
from urllib.parse import quote
import os
from app.client import client_bp

from ..models import Device, Task
from app.api import db_func
from app.api import redis_func
from app.api import ws

import traceback
import jwt
import subprocess

@client_bp.route('/user/login', methods=['POST'])
def login_dashboard():
  password = request.json.get('password')
  if password is None:
    return abort(401)
  else:
    if password == current_app.config["ADMIN_PWD"]:
      session['role'] = 'admin'
      session['uid'] = 'admin'
      return jsonify({"result": 0, "message": "success", "role": "admin"})
    else:
      return jsonify({"result": -1, "message": "用户名或密码错误"})


@client_bp.route('/user/logout', methods=["POST"])
def login():
  session.pop('role','')
  session.pop('uid','')
  return jsonify({"result": 0, 'message': "success"})


@client_bp.route('/device/register', methods=["POST"])
def register():
  try:
    uni_id = request.json.get('uni_id','')
    if uni_id == '':
      return jsonify({"result": -1, "message": "注册失败"})

    query_result, qs_count = db_func.query_device({"uni_id": uni_id})
    if qs_count == 1:
      device = query_result[0]
      uid = device["uid"]
      register_time = device["register_time"]
    else:
      name = request.json.get('name','')
      device_type = request.json.get('device_type','')
      cpu = request.json.get('cpu','')
      memory = request.json.get('memory','')
      os = request.json.get('os','')
      data_meta = request.json.get('data_meta','')
      date = datetime.now()

      device = dict(uni_id=uni_id, name=name, device_type=device_type, cpu=cpu,
                    memory=memory, os=os, data_meta=data_meta, register_time=date)
      uid, register_time = db_func.add_device(device)

    headers = {
      'alg': "HS256",  # 声明所使用的算法
    }
    auth_token = jwt.encode({'uid': uid, 'register_time': register_time},
                            current_app.config["JWT_KEY"],
                            headers=headers,
                            algorithm='HS256')

    return jsonify({"result": 0, "message": "注册成功", "value": auth_token, "uid": uid})
  except Exception as e:
    current_app.logger.error(e)
    return jsonify({"result": -2, "message": "注册失败"})


@client_bp.route('/dashboard/device/delete', methods=["POST"])
def device_delete():
  try:
    uid = request.json.get('uid','')
    if uid == '':
      return jsonify({"result": -1, "message": "注销失败"})

    db_func.delete_device(uid)

    return jsonify({"result": 0, "message": "注销成功"})
  except Exception as e:
    current_app.logger.error(e)
    return jsonify({"result": -2, "message": "注销失败"})

# @client_bp.route('/device/heart', methods=["POST"])
# def heart():
#   try:
#     uid = request.json.get('uid','')
#     if uid == '':
#       return 'Access Denied', 404
#     ip = request.json.get('ip','')
#     ping = request.json.get('ping','')
#     cpu_ing = request.json.get('cpu_ing','')
#     memory_ing = request.json.get('memory_ing','')
#     timestamp = int(datetime.now().timestamp())
#     redis_func.update_device_status(uid, dict(ip=ip,
#                                               cpu_ing=cpu_ing,
#                                               memory_ing=memory_ing,
#                                               timestamp=timestamp,
#                                               ping=ping))
#
#     return jsonify({"result": 0, "message": "success"})
#   except Exception as e:
#     current_app.logger.error(e)
#     return jsonify({"result": -1, "message": "failed"})

@client_bp.route('/dashboard/device/list', methods=["GET"])
def device_list():
  try:
    page = request.args.get('currentPage', 1)

    query_result, count = db_func.query_device({}, page=int(page))

    for d in query_result:
      res = redis_func.get_device_status(d["uid"])
      d.update(res)
      d["show"] = False

    return jsonify({"result": 0, "message": "success", "value": query_result, "count": count})

  except Exception as e:
    current_app.logger.error(e)
    return jsonify({"result": -2, "message": "failed"})

# @client_bp.route('/dashboard/task/start', methods=["POST"])
# def task_start():
#   mid = request.json.get("mid", '')
#
#   # 查询devices
#   uid = request.json.get("uid", '')
#   ws.start_task({'mid':1, 'docker_path': 'localhost'}, uid=uid)
#   return "ok"

@client_bp.route('/dashboard/task/create', methods=["POST"])
def task_create():
  try:
    info = {}
    info["name"] = request.json.get("name", '')
    info["model_type"] = request.json.get("type", '')
    info["program_info"] = request.json.get("program_info", '')
    info["devices"] = "|".join([str(i) for i in request.json.get("multipleSelection", [])])
    info["create_time"] = datetime.now()

    if info["name"] == "" or info['devices'] == "":
      return jsonify({"result": -1, "message": "failed"})

    # 解析程序相关信息
    server_info = info["program_info"]["server"]
    client_info = info["program_info"]["client"]
    client_dict = {c["object"]: c  for c in client_info}

    # 相关检查
    server_cmd = server_info["cmd"]
    server_cmd = "docker run -d --entry-point='./start_ps.sh' comp"
    server_cmd_supervisor = "docker run -d --entry-point='./start_supervisor.sh' comp"

    if server_info["format"] == "Docker镜像" and not server_cmd.startswith("docker run "):
      return jsonify({"result": -2, "message": "Docker镜像执行命令需以`docker run`开头"})

    # 添加任务
    mid = db_func.add_task(info)

    # 启动服务端(PS和Supervisor,理论上只有一个服务端，同时完成参数聚合和准确度计算的工作，这里简便起见，分开成两个)
    # PS
    docker_ip = "172.17.0.1"
    docker_port = "9876"
    add_param = " -p {}:{} -e SERVER_IP={} -e SERVER_PORT={} -e MODEL_ID={} ".format(
      docker_port, docker_port, docker_ip, docker_port, mid
    )
    server_cmd = server_cmd[:11] + add_param + server_cmd[11:]
    server_cmd_supervisor = server_cmd_supervisor[:11] + add_param + server_cmd_supervisor[11:]

    print(server_cmd)
    print(server_cmd_supervisor)
    # subprocess.run(server_cmd.split(' '), shell=True)
    # subprocess.run(server_cmd_supervisor.split(' '), shell=True)


    # 启动客户端
    success_count = 0
    # 检查用户选择的设备是否存在，是否上传了设备对应类型的客户端程序
    for uid in info["devices"].split('|'):
      item, _ = db_func.query_device({"uid": uid})

      if item:
        program = client_dict.get(item[0]["device_type"], '')
        if program != '':
          # cmd 注入
          if program["cmd"].startswith("docker run "):
            server_ip = "172.17.0.1"
            server_port = "9876"
            add_param = " -e SERVER_IP={} -e SERVER_PORT={} -e MODEL_ID={} -e WORKER_ID={} ".format(
              server_ip, server_port, mid, uid
            )

            program["cmd"] = program["cmd"][:11] + add_param + program["cmd"][11:]
            print(program["cmd"])

          program.update({"mid":mid, "name": info["name"], "model_type": info["model_type"]})
          ws.start_task(program, uid)
          success_count += 1


    return jsonify({"result": 0, "message": "success", "value": success_count})

  except Exception as e:
    traceback.print_exc()
    current_app.logger.error(e)
    return jsonify({"result": -2, "message": "failed"})


@client_bp.route('/dashboard/task/list', methods=["GET"])
def task_list():
  try:
    page = request.args.get('currentPage', 1)

    query_result, count = db_func.query_task({}, page=int(page))

    return jsonify({"result": 0, "message": "success", "value": query_result, "count": count})

  except Exception as e:
    current_app.logger.error(e)
    return jsonify({"result": -2, "message": "failed"})

@client_bp.route('/dashboard/task/query', methods=["GET"])
def task_query():
  try:
    mid = request.args.get('mid', '')
    if mid == '':
      return jsonify({"result": -1, "message": "failed"})

    query_result, count = db_func.query_task({"mid": mid})
    if count == 0:
      return jsonify({"result": -2, "message": "failed"})

    task = query_result[0]
    # 获取设备基本信息(不含实时信息，要按顺序排好，没有查到的返回{})
    uids = task["devices"].split("|")
    devices =  [{} for uid in uids]
    uid2index =  {int(uid): idx for idx, uid in enumerate(uids)}
    query_res = db_func.query_device_list(uids)
    for q in query_res:
      devices[uid2index[q["uid"]]] = q

    res = {"task": task, "devices": devices}

    return jsonify({"result": 0, "message": "success", "value": res})

  except Exception as e:
    traceback.print_exc()
    current_app.logger.error(e)
    return jsonify({"result": -3, "message": "failed"})

@client_bp.route('/dashboard/task/delete', methods=["POST"])
def task_delete():
  try:
    mid = request.json.get('mid', '')
    if mid == '':
      return 'Error', 404

    db_func.delete_task(mid)

    return jsonify({"result": 0, "message": "success"})

  except Exception as e:
    current_app.logger.error(e)
    return jsonify({"result": -2, "message": "failed"})


@client_bp.route('/dashboard/task/device/stop', methods=["POST"])
def task_device_stop():
  try:
    mid = request.json.get('mid', '')
    uid = request.json.get('uid', '')
    if mid == '' or uid == '':
      return jsonify({"result": -1, "message": "failed"})

    query_result, qs_count = db_func.query_task({'mid': mid})

    if qs_count > 0 and ws.stop_task(query_result[0], uid):
      return jsonify({"result": 0, "message": "success"})
    else:
      return jsonify({"result": -2, "message": "failed"})
  except Exception as e:
    current_app.logger.error(e)
    return jsonify({"result": -3, "message": "failed"})
