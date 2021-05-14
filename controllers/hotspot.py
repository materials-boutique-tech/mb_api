from datetime import datetime

from flask import Blueprint, Response, request, jsonify
from flask_login import login_required

from db import db
from models.Host import Host
from models.Hotspot import Hotspot
from utils.helium_api_utils import create_invoice, start_current_month
from utils.request_utils import Serializer

hotspot = Blueprint('hotspot', __name__)

def validate_unique(data):
  if Hotspot.query.filter_by(name=data['name']).first(): return False
  return not Hotspot.query.filter_by(net_add=data['net_add']).first()


# route for adding a hotspot
@hotspot.route('/add', methods=['POST'])
@login_required
def add_hotspot():
  data = request.json

  if not validate_unique(data):
    return Response('hotspot with the provided name or net address already exists', status=400,
                    mimetype='application/json')

  db.session.add(Hotspot(net_add=data['net_add'],
                         name=data['name'],
                         model=data['model']
                         ))
  db.session.commit()

  return Response('hotspot created', status=201, mimetype='application/json')


# route for updating a hotspot
@hotspot.route('/update', methods=['POST'])
@login_required
def update_hotspot():
  data = request.json
  _hotspot = Hotspot.query.get(data['id'])
  _hotspot.name = data['name'].lower(),
  _hotspot.net_add = data['net_add']
  _hotspot.model = data['model']

  db.session.commit()

  return Response('hotspot updated', status=200, mimetype='application/json')


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

  if str(_hotspot.host_id) == host_id:  # make sure they have the correct host
    _hotspot.host_id = None
    host = Host.query.get(host_id)
    db.session.commit()

    success_res = Response('hotspot removed from host', status=200, mimetype='application/json')

    # the invoice generation running on scheduler stops at end of prev month so
    # when removing we create the partial invoice for the current month
    last_txd = _hotspot.serialize()['last_transferred']
    now = datetime.utcnow()

    same_month_and_year = last_txd.month == now.month and last_txd.year == now.year

    # need to handle case when the hotspot was transferred to host and removed from
    # that host within the same month
    if same_month_and_year:
      # if transferred and removed on the same day do not generate invoice
      if last_txd.day == now.day:
        return Response(
          'hotspot removed from host; hotspot was assigned within 24 hours of being removed - no invoice generated',
          status=200, mimetype='application/json')

      # if it was transferred in the current month transfer date is the start_date of the invoice
      create_invoice(_hotspot, host, last_txd, now)
      return success_res

    # otherwise it was transferred in a prev month and the start_range for the invoice
    # is the start of the current month
    create_invoice(_hotspot, host, start_current_month(), now)
    return success_res

  return Response('the specified hotspot has a different host', status=400, mimetype='application/json')


# admin route for getting a single hotspot
@hotspot.route('/hotspot', methods=['GET'])
@login_required
def get_host():
  return Hotspot.query.get(request.args.get('hotspot_id')).serialize()


