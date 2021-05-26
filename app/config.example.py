"""
Global Flask Application Setting

See `.flaskenv` for default settings.
 """

import os
from app import app


class Config(object):
    # If not set fall back to production for safety
    FLASK_ENV =  os.getenv('FLASK_ENV', 'production')
    print("FLASK_ENV:", FLASK_ENV)
    # Set FLASK_SECRET on your production Environment
    SECRET_KEY = os.getenv('FLASK_SECRET', 'Secret')
    # Mysql config
    HOST = os.getenv('MYSQL_HOST', '')
    PORT = os.getenv('MYSQL_PORT', '3306')
    DATABASE = os.getenv('MYSQL_DATABASE', 'grad')
    USERNAME = os.getenv('MYSQL_USERNAME', 'root')
    PASSWORD = os.getenv('MYSQL_PASSWORD', '')

    APP_DIR = os.path.dirname(__file__)
    ROOT_DIR = os.path.dirname(APP_DIR)
    DIST_DIR = os.path.join(ROOT_DIR, 'dist')
    UPLOAD_DIR = os.path.join(ROOT_DIR, 'upload')

    DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=USERNAME,
                                                                                            password=PASSWORD,
                                                                                            host=HOST, port=PORT,
                                                                                            db=DATABASE)
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)
    REDIS_PWD = os.getenv('REDIS_PWD', "")

    # auth key setting
    AUTH_KEY = "authorized"

    # admin pwd
    ADMIN_PWD = ""
    PRIVATE_KEY = ""

    # JWT KEY
    JWT_KEY = ""

    SERVER_IP = "192.168.1.184"
    SERVER_PORT = "9876"
    
    if not os.path.exists(DIST_DIR):
        raise Exception(
            'DIST_DIR not found: {}'.format(DIST_DIR))

app.config.from_object('app.config.Config')
