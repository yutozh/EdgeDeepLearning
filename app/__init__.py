import os
from flask import Flask, current_app, send_file, request, current_app, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask_socketio import SocketIO

from flask_cors import CORS
import hashlib
import logging
import redis

app = Flask(__name__, static_folder='../dist/static', static_url_path='/static')
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, supports_credentials=True)
db = SQLAlchemy()

from app.config import Config
r = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, password=Config.REDIS_PWD, decode_responses=True)

from .client import client_bp
app.register_blueprint(client_bp)

logging.basicConfig(level=logging.DEBUG)
handler = logging.FileHandler('logs/flask.log', encoding='UTF-8')
logging_format = logging.Formatter(    # 设置日志格式
  '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

app.config.from_object(Config)


# database initialize
db.init_app(app)
app.app_context().push()

engine = create_engine(Config.DB_URI)
if not database_exists(engine.url):
  create_database(engine.url)
db.create_all()
db.session.commit()


# home and auth route
@current_app.route('/')
def index_client():
  dist_dir = current_app.config['DIST_DIR']
  entry = os.path.join(dist_dir, 'index.html')
  return send_file(entry)

