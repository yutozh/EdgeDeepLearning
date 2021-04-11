""" Client App """

import os
from flask import Blueprint, render_template

client_bp = Blueprint('client_app', __name__,
                      url_prefix='/api',
                      static_url_path='',
                      static_folder='./dist/static/',
                      template_folder='./dist/',
                      )

@client_bp.after_request
def add_header(response):
  response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
  return response


# Import resources to ensure view is registered
from app.api.dashboard import * # NOQA
from app.api.ws import * # NOQA

