from db import db
from models.mixins.CoreMixin import CoreMixin
from utils.api_error import FormError
from utils.request_utils import Serializer
from utils.validation_utils import type_name, type_email, type_phone, type_city_or_state, max_length, required_length, \
  type_zip_code, one_of, type_bool, min_length
from utils.validation_utils import validate

HNT = 'hnt'
BANK_ACCOUNT = 'bank_account'
VENMO = 'venmo'


class Host(db.Model, CoreMixin, Serializer):
  first_name = db.Column(db.String(80), nullable=False)
  last_name = db.Column(db.String(120), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  street = db.Column(db.String(120), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  zip = db.Column(db.String(120), nullable=False)
  w9_received = db.Column(db.Boolean, server_default='false', nullable=False)
  payment_method = db.Column(db.String(120), server_default=HNT, nullable=False)
  hnt_wallet = db.Column(db.String(120))
  bank_account_number = db.Column(db.String(120))
  bank_routing_number = db.Column(db.String(120))
  venmo_handle = db.Column(db.String(120))

  host_assignments = db.relationship("Assignment", backref="host", foreign_keys='Assignment.host_id')
  referral_assignments = db.relationship("Assignment", backref="referer", foreign_keys='Assignment.referer_id')
  host_invoices = db.relationship('HostInvoice', backref='host')

  validation = {
    'first_name': [type_name],
    'last_name': [type_name],
    'email': [type_email],
    'phone': [type_phone],
    'street': [max_length(120)],
    'city': [type_city_or_state],
    'state': [type_city_or_state],
    'zip': [type_zip_code],
    'w9_received': [type_bool],
    'payment_method': [one_of([HNT, BANK_ACCOUNT, VENMO])],
    'hnt_wallet': [required_length(51)],
    'bank_account_number': [min_length(6), max_length(24)],
    'bank_routing_number': [min_length(6), max_length(24)],
    'venmo_handle': [],
  }

  def serialize(self):
    return {'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'hnt_wallet': self.hnt_wallet,
            'w9_received': self.w9_received,
            'payment_method': self.payment_method,
            'bank_account_number': self.bank_account_number,
            'bank_routing_number': self.bank_routing_number,
            'venmo_handle': self.venmo_handle,
            'id': self.id
            }

  def eligible_to_be_referred(self, assignment_being_edited_id):
    # if the host has never had an assignment
    if self.host_assignments is None or not len(self.host_assignments): return True

    # if the host being referred has only one active assignment and it is the one being edited
    if len(self.host_assignments) == 1 and \
      self.host_assignments[0].is_active() and \
      str(self.host_assignments[0].id) == str(assignment_being_edited_id):
      return True

    return False

  @staticmethod
  def make_new(data):
    if Host.email_in_use(data): raise FormError('host with the provided email already exists')

    validate(data, Host.validation)

    # noinspection PyArgumentList
    h = Host(email=data['email'],
             first_name=data['first_name'],
             last_name=data['last_name'],
             phone=data['phone'],
             street=data['street'],
             city=data['city'],
             state=data['state'],
             zip=data['zip'],
             payment_method=data['payment_method'])

    return Host.host_payment_details(h, data)

  @staticmethod
  def update(data):
    validate(data, Host.validation)
    h = Host.query.get(data['id'])

    h.email = data['email'],
    h.first_name = data['first_name']
    h.last_name = data['last_name']
    h.phone = data['phone']
    h.street = data['street']
    h.city = data['city']
    h.state = data['state']
    h.zip = data['zip']
    h.w9_received = data['w9_received']
    h.payment_method = data['payment_method']  # changes apply to entire month

    Host.host_payment_details(h, data)
    db.session.commit()

  @staticmethod
  def by_id(host_id):
    return Host.query.get(host_id)

  @staticmethod
  def email_in_use(data):
    return Host.query.filter_by(email=data['email']).first()

  # TODO: shouldn't be static
  @staticmethod
  def host_payment_details(_host, data):
    method = data['payment_method']

    if method == HNT:
      _host.hnt_wallet = data['hnt_wallet']
    if method == BANK_ACCOUNT:
      _host.bank_account_number = data['bank_account_number']
      _host.bank_routing_number = data['bank_routing_number']
    if method == VENMO:
      _host.venmo_handle = data['venmo_handle']
    return _host
