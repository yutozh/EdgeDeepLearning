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
from app.api import launch

import traceback
import jwt
import subprocess

server_docker_name_map = {}
supervisor_docker_name_map = {}

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
    user_server_cmd = server_info["cmd"]
    # server_cmd = "docker run -d  comp"
    # server_cmd_supervisor = "docker run -d  comp"

    if server_info["format"] == "Docker镜像" and not user_server_cmd.startswith("docker run "):
      return jsonify({"result": -2, "message": "Docker镜像执行命令需以`docker run`开头"})

    # 添加任务
    mid = db_func.add_task(info)

    # 启动服务端(PS和Supervisor,理论上只有一个服务端，同时完成参数聚合和准确度计算的工作，这里简便起见，分开成两个)
    # PS
    server_ip = current_app.config["SERVER_IP"]
    server_port = int(current_app.config["SERVER_PORT"]) + int(mid) % 65535

    launch.launch_server(user_server_cmd, server_ip, server_port, mid)
    success_count = launch.launch_client(info["devices"].split('|'), client_dict, server_ip, server_port,
                                         mid, info["name"], info["model_type"])
    #
    # server_docker_name = "server_{}".format(mid)
    # supervisor_docker_name = "supervisor_{}".format(mid)
    #
    # add_param_server = " -p {}:{} -e SERVER_IP={} -e SERVER_PORT={} -e MODEL_ID={} --name {} --entrypoint='./start_ps.sh' ".format(
    #   server_port, server_port, server_ip, server_port, mid, server_docker_name
    # )
    # server_cmd = user_server_cmd[:11] + add_param_server + user_server_cmd[11:]
    # add_param_supervisor = " -e SERVER_IP={} -e SERVER_PORT={} -e MODEL_ID={} --name {} --entrypoint='./start_supervisor.sh' ".format(
    #   server_ip, server_port, mid, supervisor_docker_name
    # )
    #
    # server_cmd_supervisor = user_server_cmd[:11] + add_param_supervisor + user_server_cmd[11:]
    #
    # print(server_cmd)
    # print(server_cmd_supervisor)
    # subprocess.run(server_cmd, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    # subprocess.run(server_cmd_supervisor, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    #
    #
    # # 启动客户端
    # success_count = 0
    # # 检查用户选择的设备是否存在，是否上传了设备对应类型的客户端程序
    # for uid in info["devices"].split('|'):
    #   item, _ = db_func.query_device({"uid": uid})
    #   if item: # 设备存在
    #     device_type = item[0]["device_type"]
    #     program = client_dict.get(device_type, '')
    #     if program != '': # 对应程序存在
    #       # cmd 注入
    #       if program["cmd"].startswith("docker run "):
    #
    #         add_param = " -e SERVER_IP={} -e SERVER_PORT={} -e MODEL_ID={} -e WORKER_ID={} ".format(
    #           server_ip, server_port, mid, uid
    #         )
    #
    #         program["cmd"] = program["cmd"][:11] + add_param + program["cmd"][11:]
    #         print(program["cmd"])
    #
    #       program.update({"mid":mid, "name": info["name"], "model_type": info["model_type"]})
    #       print(program)
    #       ws.start_task(program, uid)
    #       success_count += 1

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

    for t in query_result:
      devices = t["devices"].split("|")
      t["devices_running"] = 0
      t["devices_starting"] = 0
      t["devices_stopped"] = 0
      for uid in devices:
        device_status = str(redis_func.get_device_model_status(uid, t["mid"]))
        if device_status == '1':
          t['devices_running'] += 1
        if device_status == '0':
          t['devices_starting'] += 1
        if device_status == '-1':
          t['devices_stopped'] += 1

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

@client_bp.route('/dashboard/task/start', methods=["POST"])
def task_start():
  try:
    mid = request.json.get('mid', '')
    if mid == '':
      return jsonify({"result": -1, "message": "failed"})

    query_result, qs_count = db_func.query_task({'mid': mid})
    if qs_count == 0:
      return jsonify({"result": -2, "message": "任务未找到"})

    task_item = query_result[0]
    if task_item["status"] == "正在训练":
      return jsonify({"result": -2, "message": "任务已启动"})

    program_info = query_result[0]["program_info"]

    # 解析程序相关信息
    server_info = program_info["server"]
    client_info = program_info["client"]
    client_dict = {c["object"]: c for c in client_info}

    # 相关检查
    user_server_cmd = server_info["cmd"]
    # server_cmd = "docker run -d  comp"
    # server_cmd_supervisor = "docker run -d  comp"

    # 启动服务端(PS和Supervisor,理论上只有一个服务端，同时完成参数聚合和准确度计算的工作，这里简便起见，分开成两个)
    # PS
    server_ip = current_app.config["SERVER_IP"]
    server_port = int(current_app.config["SERVER_PORT"]) + int(mid) % 65535

    launch.restart_server(mid)
    success_count = launch.launch_client(task_item["devices"].split('|'), client_dict, server_ip, server_port,
                         mid, task_item["name"], task_item["model_type"])

    # 更新状态
    db_func.update_task(mid, {'status': '正在训练', 'end_time': None})

    return jsonify({"result": 0, "message": "success", "value": success_count})

  except Exception as e:
    traceback.print_exc()
    current_app.logger.error(e)
    return jsonify({"result": -2, "message": "failed"})

@client_bp.route('/dashboard/task/stop', methods=["POST"])
def task_stop():
  try:
    mid = request.json.get('mid', '')
    if mid == '':
      return jsonify({"result": -1, "message": "failed"})

    launch.stop_server(mid)
    launch.stop_client(mid)

    db_func.update_task(mid, {'status': '训练停止', 'end_time': datetime.now()})

    return jsonify({"result": 0, "message": "success"})

  except Exception as e:
    current_app.logger.error(e)
    return jsonify({"result": -2, "message": "failed " + str(e)})

@client_bp.route('/dashboard/task/delete', methods=["POST"])
def task_delete():
  try:
    mid = request.json.get('mid', '')
    if mid == '':
      return 'Error', 404

    query_result, qs_count = db_func.query_task({'mid': mid})
    if qs_count == 0:
      return jsonify({"result": -1, "message": "未找到任务"})

    if query_result[0]['status'] != '训练停止':
      return jsonify({"result": -2, "message": "请先停止训练,再删除任务"})

    launch.delete_server(mid) # 删除server的容器, client的在停止时已经删除
    db_func.delete_task(mid)

    return jsonify({"result": 0, "message": "success"})

  except Exception as e:
    current_app.logger.error(e)
    return jsonify({"result": -3, "message": "failed"})


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
