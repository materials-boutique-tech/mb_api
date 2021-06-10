from flask import Blueprint, Response, request, jsonify
from flask_login import login_required

from db import db
from models.Host import Host
from utils.request_utils import Serializer

host = Blueprint('host', __name__)


# admin route for getting all hosts
@host.route('/', methods=['GET'])
@login_required
def index():
  _hosts = Host.query.all()
  return jsonify(Serializer.serialize_list(_hosts))


# admin route for getting a single host
@host.route('/host', methods=['GET'])
@login_required
def show():
  return Host.by_id(request.args.get('host_id')).serialize()


# public facing signup route (no login required) - allows a host to enter
# their info but cannot set w9 status
@host.route('/signup', methods=['POST'])
def signup_host():
  new_host = Host.make_new(request.json)
  db.session.add(new_host)
  db.session.commit()
  return Response('submit success', status=201, mimetype='application/json')


# admin route for adding a host - can set w9 bool
@host.route('/add', methods=['POST'])
@login_required
def add_host():
  data = request.json
  new_host = Host.make_new(data)

  if 'w9_received' in data:
    new_host.w9_received = data['w9_received']

  db.session.add(new_host)
  db.session.commit()
  return Response('Host {} {} created'.format(new_host.first_name, new_host.last_name),
                  status=201, mimetype='application/json')


# admin route for updating a host
@host.route('/update', methods=['POST'])
@login_required
def update_host():
  Host.update(request.json)
  return Response('host updated', status=200, mimetype='application/json')
