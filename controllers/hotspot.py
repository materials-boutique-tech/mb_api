from flask import Blueprint, Response, request, jsonify
from flask_login import login_required
from db import db
from models.Hotspot import Hotspot
from models.Host import Host
from utils.request_utils import Serializer
from utils.helium_api_utils import create_invoice, start_current_month
from datetime import datetime
hotspot = Blueprint('hotspot', __name__)


@hotspot.route('/add', methods=['POST'])
@login_required
def add_hotspot():
  data = request.json

  already_exists = Hotspot.query.filter_by(name=data['name']).first()

  if already_exists:
    return Response('hotspot with the provided name already exists', status=401,
                    mimetype='application/json')

  db.session.add(Hotspot(email=data['email'],
                         first_name=data['first_name'],
                         last_name=data['last_name'],
                         phone=data['phone'],
                         street=data['street'],
                         city=data['city'],
                         state=data['state'],
                         zip=data['zip'],
                         hnt_wallet=data['hnt_wallet']))
  db.session.commit()

  return Response('hotspot created', status=201, mimetype='application/json')


# returns all hotspots
@hotspot.route('/', methods=['GET'])
@login_required
def index():
  _hotspots = Hotspot.query.all()
  return jsonify(Serializer.serialize_list(_hotspots))


# returns all hotspots not assigned to a host
@hotspot.route('/unassigned', methods=['GET'])
@login_required
def hotspots_without_host():
  # time.sleep(3)
  _hotspots = Hotspot.query.filter_by(host_id=None)
  return jsonify(Serializer.serialize_list(_hotspots))


# returns all hotspots assigned to a host
@hotspot.route('/by-host', methods=['GET'])
@login_required
def hotspots_for_host():
  _hotspots = Hotspot.query.filter_by(host_id=request.args.get('host_id'))
  return jsonify(Serializer.serialize_list(_hotspots))


# remove hotspot from a host
@hotspot.route('/remove-host', methods=['POST'])
@login_required
def remove_hotspot_host():
  host_id = request.json['host_id']
  _hotspot = Hotspot.query.get(request.json['hotspot_id'])


  if str(_hotspot.host_id) == host_id: # make sure they have the correct host
    host = Host.query.get(host_id)
    create_invoice(_hotspot, host, start_current_month(), datetime.utcnow())

    _hotspot.host_id = None
    db.session.commit()
    return Response('hotspot removed from host', status=200, mimetype='application/json')

  return Response('the specified hotspot has a different host', status=400, mimetype='application/json')
