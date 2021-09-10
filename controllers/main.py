import os

from flask import Blueprint, Response, request, jsonify
from flask_login import login_required

from db import db
from seed.seed import seed_all, seed_users

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def hello_world():
  return 'Welcome to the Materials Boutique API'


@main.route('/seed', methods=['GET'])
@login_required
def seed():
  seed_all()
  return Response('seed complete', status=201, mimetype='application/json')


@main.route('/seed-users', methods=['GET'])
def _seed_users():
  seed_users()
  return Response('seed users complete', status=201, mimetype='application/json')


@main.route('/version', methods=['GET'])
def app_version():
  with open("semver.txt", "r") as semver_file:
    version = semver_file.readlines()[0].strip()
  return jsonify(version=version)


@main.route('/drop-all', methods=['GET'])
@login_required
def drop_all():
  if os.environ['APP_SETTINGS'] != 'development':
    confirmation_query_param = request.args.get('confirmation')
    do_seed = request.args.get('do_seed')

    if confirmation_query_param == 'confirm_drop_all':
      db.drop_all()
      db.create_all()

      if do_seed == 'true':
        seed_all()
        return Response('dropped all tables and ran seed', status=200, mimetype='application/json')

      return Response('dropped all tables', status=200, mimetype='application/json')
    return Response('incorrect or missing confirmation', status=400, mimetype='application/json')
