from app import r
from flask import jsonify, current_app, session

def update_device_status(uid, info):
  r.hmset("device-{}".format(uid), info)

def update_device_model_status(uid, mid, status):
  r.hset("model_device-{}".format(mid), uid, status)

def get_device_status(uid):
  res = r.hgetall("device-{}".format(uid))
  return res

def get_device_wsid(uid):
  res = r.hget("device-{}".format(uid), 'sid')
  return res

def get_device_model_status(uid, mid):
  res = r.hget("model_device-{}".format(mid), uid)
  return 0 if res == None else res

def get_model_status(mid):
  res_0 = r.lrange("model-{}-iter".format(mid), -30, -1)
  res_1 = r.lrange("model-{}-accu".format(mid), -30, -1)
  res_2 = r.lrange("model-{}-loss".format(mid), -30, -1)

  return {"iter": res_0, "accu": res_1, "loss": res_2}

def get_device_model_contribute_time(uid, mid):
  res = r.get("contribute-{}-{}".format(uid, mid))
  return res

def test():
  r.lpush("model-1-loss", 1.1)
  r.lpush("model-1-loss", 1.0)
  print(r.lrange("model-1-loss", -5, -1))
