from flask import Blueprint, Response, request, jsonify
from models.Hotspot import Hotspot
from flask_login import login_required
from db import db
from models.Host import Host
from utils.request_utils import Serializer
import datetime
from utils.helium_api_utils import start_day

host = Blueprint('host', __name__)


@host.route('/add', methods=['POST'])
@login_required
def add_host():
  data = request.json

  already_exists = Host.query.filter_by(email=data['email']).first()

  if already_exists:
    return Response('host with the provided email already exists', status=401,
                    mimetype='application/json')

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

  for hotspot_id in data['hotspot']:
    hs = Hotspot.query.get(hotspot_id)

    if "transfer_date" in data:
      hs.last_transferred =  data['transfer_date']
    else:
      hs.last_transferred = start_day(datetime.datetime.now())

    new_host.hotspots.append(hs)

  db.session.add(new_host)
  db.session.commit()

  return Response('host created', status=201, mimetype='application/json')


@host.route('/', methods=['GET'])
@login_required
def index():
  _hosts = Host.query.all()
  return jsonify(Serializer.serialize_list(_hosts))
