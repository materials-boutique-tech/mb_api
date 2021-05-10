from flask import Blueprint, Response, request, jsonify
from models.Hotspot import Hotspot
from flask_login import login_required
from db import db
from models.Host import Host
from utils.request_utils import already_exist_error
import datetime
from utils.helium_api_utils import start_day
from utils.request_utils import Serializer

host = Blueprint('host', __name__)


# the signup route is public facing (no login required) - allows a host to enter
# their info but does not support assigning hotspots or changing w9_received status
@host.route('/signup', methods=['POST'])
def signup_host():
  data = request.json
  if check_already_exists(data): return already_exist_error('host')

  # noinspection PyArgumentList
  new_host = Host(email=data['email'],
                  first_name=data['first_name'],
                  last_name=data['last_name'],
                  phone=data['phone'],
                  street=data['street'],
                  city=data['city'],
                  state=data['state'],
                  zip=data['zip'],
                  hnt_wallet=data['hnt_wallet'])

  db.session.add(new_host)
  db.session.commit()

  return Response('submitted', status=201, mimetype='application/json')


# admin route for adding a host (includes w9 status and option to assign hotspots)
# TODO: how to address t&c when an admin adds host
@host.route('/add', methods=['POST'])
@login_required
def add_host():
  data = request.json
  if check_already_exists(data): return already_exist_error('host')

  # noinspection PyArgumentList
  new_host = Host(email=data['email'],
                  first_name=data['first_name'],
                  last_name=data['last_name'],
                  phone=data['phone'],
                  street=data['street'],
                  city=data['city'],
                  state=data['state'],
                  zip=data['zip'],
                  hnt_wallet=data['hnt_wallet'],
                  reward_percentage=data['reward_percentage'])

  assign_hotspots_to_host(new_host, data)

  db.session.add(new_host)
  db.session.commit()

  return Response('host created', status=201, mimetype='application/json')


# admin route for updating a host
@host.route('/update', methods=['POST'])
@login_required
def update_host():
  data = request.json
  _host = Host.query.filter_by(email=data['email']).first()

  _host.email = data['email'],
  _host.first_name = data['first_name']
  _host.last_name = data['last_name']
  _host.phone = data['phone']
  _host.street = data['street']
  _host.city = data['city']
  _host.state = data['state']
  _host.zip = data['zip']
  _host.hnt_wallet = data['hnt_wallet']
  _host.w9_received = data['w9_received']
  _host.reward_percentage = data['reward_percentage'] # changes apply to entire month

  assign_hotspots_to_host(_host, data)
  db.session.commit()

  return Response('host updated', status=200, mimetype='application/json')


# admin route for getting a single host
@host.route('/host', methods=['GET'])
@login_required
def get_host():
  return Host.query.get(request.args.get('host_id')).serialize()


# admin route for getting all hosts
@host.route('/', methods=['GET'])
@login_required
def index():
  _hosts = Host.query.all()
  return jsonify(Serializer.serialize_list(_hosts))


# helpers
def assign_hotspots_to_host(_host, data):
  if 'hotspots' in data:
    for hotspot_id in data['hotspots']:
      hs = Hotspot.query.get(hotspot_id)

      if hs.host_id:
        return Response('hotspot is assigned to another host', status=400,
                        mimetype='application/json')

      if "transfer_date" in data:
        hs.last_transferred = data['transfer_date']
      else:
        hs.last_transferred = start_day(datetime.datetime.utcnow())
      _host.hotspots.append(hs)


def check_already_exists(data):
  Host.query.filter_by(email=data['email']).first()
