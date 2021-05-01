from flask import Blueprint, Response, request, jsonify
from flask_login import login_required
from db import db
from models.Hotspot import Hotspot
from utils.request_utils import Serializer

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


@hotspot.route('/', methods=['GET'])
@login_required
def index():
  _hotspots = Hotspot.query.all()
  return jsonify(Serializer.serialize_list(_hotspots))
