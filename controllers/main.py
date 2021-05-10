import os

from flask import Blueprint, Response,send_file, send_from_directory
from flask_login import login_required
from seed.seed import seed_users, seed_hosts, seed_hotspots
from utils.path_utils import APP_STATIC
main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def hello_world():
  return 'hello world'


@main.route('/host-agreement', methods=['GET'])
def show_static_pdf():
  return send_from_directory(directory=os.path.join(APP_STATIC),
                      filename='host_agreement.pdf',
                      mimetype='application/pdf')




@main.route('/seed', methods=['GET'])
@login_required
def seed():
  seed_users()
  seed_hosts()
  seed_hotspots()
  return Response('seed complete', status=201, mimetype='application/json')
