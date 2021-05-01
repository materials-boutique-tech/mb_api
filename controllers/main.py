from flask import Blueprint, Response
from flask_login import login_required
from seed.seed import seed_users, seed_hosts, seed_hotspots

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def hello_world():
  return 'hello world'


@main.route('/seed', methods=['GET'])
@login_required
def seed():
  seed_users()
  seed_hosts()
  seed_hotspots()
  return Response('seed complete', status=201, mimetype='application/json')
