import datetime

from flask import Blueprint, Response, request, jsonify
from flask_login import login_required

from db import db
from models.Host import Host, HNT, BANK_ACCOUNT, VENMO
from models.Hotspot import Hotspot
from utils.helium_api_utils import start_day
from utils.request_utils import Serializer, form_submission_error
from utils.request_utils import already_exist_error
from utils.validation_utils import date_string_format, validate

host = Blueprint('host', __name__)


# the signup route is public facing (no login required) - allows a host to enter
# their info but does not support assigning hotspots or changing w9_received status
@host.route('/signup', methods=['POST'])
def signup_host():
  data = request.json
  if check_email_in_use(data): return already_exist_error('host', 'email')

  valid, err_msg = validate(data, Host.validation)
  if not valid: return form_submission_error(err_msg)

  # noinspection PyArgumentList
  new_host = Host(email=data['email'],
                  first_name=data['first_name'],
                  last_name=data['last_name'],
                  phone=data['phone'],
                  street=data['street'],
                  city=data['city'],
                  state=data['state'],
                  zip=data['zip'],
                  payment_method=data['payment_method'])

  update_host_payment_details(new_host, data)

  db.session.add(new_host)
  db.session.commit()

  return Response('submitted', status=201, mimetype='application/json')


# admin route for adding a host (includes w9 status and option to assign hotspots)
# TODO: how to address t&c when an admin adds host?
@host.route('/add', methods=['POST'])
@login_required
def add_host():
  data = request.json
  if check_email_in_use(data): return already_exist_error('host', 'email')

  valid, err_msg = validate(data, Host.validation)
  if not valid: return form_submission_error(err_msg)

  # noinspection PyArgumentList
  new_host = Host(email=data['email'],
                  first_name=data['first_name'],
                  last_name=data['last_name'],
                  phone=data['phone'],
                  street=data['street'],
                  city=data['city'],
                  state=data['state'],
                  zip=data['zip'],
                  reward_percentage=data['reward_percentage'],
                  w9_received=data['w9_received'],
                  payment_method=data['payment_method'])

  update_host_payment_details(new_host, data)
  err = assign_hotspots_to_host(new_host, data)
  if err: return err

  db.session.add(new_host)
  db.session.commit()

  return Response('host created', status=201, mimetype='application/json')


# admin route for updating a host
@host.route('/update', methods=['POST'])
@login_required
def update_host():
  data = request.json

  valid, err_msg = validate(data, Host.validation)
  if not valid: return form_submission_error(err_msg)

  _host = Host.query.get(data['id'])

  _host.email = data['email'],
  _host.first_name = data['first_name']
  _host.last_name = data['last_name']
  _host.phone = data['phone']
  _host.street = data['street']
  _host.city = data['city']
  _host.state = data['state']
  _host.zip = data['zip']
  _host.w9_received = data['w9_received']
  _host.reward_percentage = data['reward_percentage']  # changes apply to entire month
  _host.payment_method = data['payment_method']  # changes apply to entire month

  update_host_payment_details(_host, data)
  err = assign_hotspots_to_host(_host, data)
  if err: return err

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
# TODO: check that no invoice record exists for hotspot with date after transfer date?
# tho we do already check for existing invoice with hotspot name and startdate
def assign_hotspots_to_host(_host, data):
  if 'hotspots' in data:
    for hotspot_id in data['hotspots']:
      hs = Hotspot.query.get(hotspot_id)

      if hs.host_id:
        return Response('hotspot is assigned to another host', status=400,
                        mimetype='application/json')

      if "transfer_date" in data:
        if date_string_format("transfer_date", data):
          return form_submission_error('transfer date should be in format mm/dd/yy')
        hs.last_transferred = data['transfer_date']
      else:
        hs.last_transferred = start_day(datetime.datetime.utcnow())
      _host.hotspots.append(hs)
  return None


def update_host_payment_details(_host, data):
  method = data['payment_method']

  if method == HNT:
    _host.hnt_wallet = data['hnt_wallet']
  if method == BANK_ACCOUNT:
    _host.bank_account_number = data['bank_account_number']
    _host.bank_routing_number = data['bank_routing_number']
  if method == VENMO:
    _host.venmo_handle = data['venmo_handle']



def check_email_in_use(data):
  return Host.query.filter_by(email=data['email']).first()
