from flask import Blueprint, Response, request, jsonify
from flask_login import login_required

from models.Hotspot import Hotspot
from utils.request_utils import Serializer

hotspot = Blueprint('hotspot', __name__)


@hotspot.route('/add', methods=['POST'])
@login_required
def add_hotspot():
  Hotspot.add(request.json)
  return Response('hotspot created', status=201, mimetype='application/json')


@hotspot.route('/update', methods=['POST'])
@login_required
def update_hotspot():
  Hotspot.update(request.json)
  return Response('hotspot updated', status=200, mimetype='application/json')


@hotspot.route('/', methods=['GET'])
@login_required
def index():
  return jsonify(Serializer.serialize_list(Hotspot.all_hotspots()))


@hotspot.route('/unassigned', methods=['GET'])
@login_required
def unassigned_hotspots():
  _hotspots = Hotspot.query.all()  # unassigned()

  return jsonify([
    {'name': hs.name,
     'id': str(hs.id),
     'net_add': hs.net_add,
     'model': hs.model,
     }
    for hs in _hotspots])


@hotspot.route('/hotspot', methods=['GET'])
@login_required
def get_hotspot():
  return Hotspot.query.get(request.args.get('hotspot_id')).serialize()
