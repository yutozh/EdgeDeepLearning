#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Date: 2021/4/12 下午7:52
# @Filename: launch_server
# @Author：zyt
import subprocess
from app.api import db_func, ws

def launch_server(user_server_cmd, server_ip, server_port, mid):
  server_docker_name = "server_{}".format(mid)
  supervisor_docker_name = "supervisor_{}".format(mid)

  add_param_server = " -p {}:{} -e SERVER_IP={} -e SERVER_PORT={} -e MODEL_ID={} --name {} --entrypoint='./start_ps.sh' ".format(
    server_port, server_port, server_ip, server_port, mid, server_docker_name
  )
  server_cmd = user_server_cmd[:11] + add_param_server + user_server_cmd[11:]
  add_param_supervisor = " -e SERVER_IP={} -e SERVER_PORT={} -e MODEL_ID={} --name {} --entrypoint='./start_supervisor.sh' ".format(
    server_ip, server_port, mid, supervisor_docker_name
  )

  server_cmd_supervisor = user_server_cmd[:11] + add_param_supervisor + user_server_cmd[11:]

  print(server_cmd)
  print(server_cmd_supervisor)
  subprocess.run("docker rm -f {}".format(server_docker_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  subprocess.run("docker rm -f {}".format(supervisor_docker_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  subprocess.run(server_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  subprocess.run(server_cmd_supervisor, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  return True

def restart_server(mid):
  server_docker_name = "server_{}".format(mid)
  supervisor_docker_name = "supervisor_{}".format(mid)

  subprocess.run("docker start  {}".format(server_docker_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  subprocess.run("docker start  {}".format(supervisor_docker_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  return True

def launch_client(uids, client_dict, server_ip, server_port, mid, task_name, model_type):
  # 启动客户端
  success_count = 0
  # 检查用户选择的设备是否存在，是否上传了设备对应类型的客户端程序
  for uid in uids:
    item, _ = db_func.query_device({"uid": uid})
    if item:  # 设备存在
      device_type = item[0]["device_type"]
      program = client_dict.get(device_type, '')
      if program != '':  # 对应程序存在
        # cmd 注入
        if program["cmd"].startswith("docker run "):
          add_param = " -e SERVER_IP={} -e SERVER_PORT={} -e MODEL_ID={} -e WORKER_ID={} ".format(
            server_ip, server_port, mid, uid
          )

          program["cmd"] = program["cmd"][:11] + add_param + program["cmd"][11:]
          print(program["cmd"])

        program.update({"mid": mid, "name": task_name, "model_type": model_type})
        ws.start_task(program, uid)
        success_count += 1
  return success_count

def stop_server(mid):
  server_docker_name = "server_{}".format(mid)
  supervisor_docker_name = "supervisor_{}".format(mid)
  subprocess.run("docker stop {} &".format(server_docker_name), shell=True, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)
  subprocess.run("docker stop {} &".format(supervisor_docker_name), shell=True, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)


def stop_client(mid):
  query_result, qs_count = db_func.query_task({'mid': mid})
  if qs_count == 0:
    raise Exception("No mid ", mid)
  uids = query_result[0]["devices"].split('|')
  for uid in uids:
    ws.stop_task(query_result[0], uid)


def delete_server(mid):
  server_docker_name = "server_{}".format(mid)
  supervisor_docker_name = "supervisor_{}".format(mid)
  subprocess.run("docker rm -f {} &".format(server_docker_name), shell=True, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)
  subprocess.run("docker rm -f {} &".format(supervisor_docker_name), shell=True, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)

