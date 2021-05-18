from db import db
from models.mixins.CoreMixin import CoreMixin
from utils.request_utils import Serializer
from utils.validation_utils import type_name, type_email, type_phone, type_city_or_state, max_length, required_length, \
  type_zip_code, one_of, type_bool, type_string, number_in_range

# two options for how we compensate hosts
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
  bank_account_number = db.Column(db.String(120))
  bank_routing_number = db.Column(db.String(120))
  venmo_handle = db.Column(db.String(120))
  hnt_wallet = db.Column(db.String(120))
  w9_received = db.Column(db.Boolean, server_default='false', nullable=False)
  reward_percentage = db.Column(db.Integer, server_default='50', nullable=False)
  payment_method = db.Column(db.String(120), server_default=HNT, nullable=False)
  hotspots = db.relationship('Hotspot', backref='host', lazy=True)
  invoices = db.relationship('Invoice', backref='host', lazy=True)

  validation = {
    'first_name': [type_name, type_string],
    'last_name': [type_name, type_string],
    'email': [type_email, type_string],
    'phone': [type_phone, type_string],
    'street': [max_length(120), type_string],
    'city': [type_city_or_state, type_string],
    'state': [type_city_or_state, type_string],
    'zip': [type_zip_code, type_string],
    'hnt_wallet': [required_length(51), type_string],
    'w9_received': [type_bool],
    'reward_percentage': [number_in_range(1, 100)],
    'payment_method': [one_of([HNT, BANK_ACCOUNT, VENMO]), type_string],
    'bank_account_number': [type_string],
    'bank_routing_number': [type_string],
    'venmo_handle': [type_string],
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
            'hotspots': Serializer.serialize_list(self.hotspots),
            'hotspot_count': len(self.hotspots),
            'w9_received': self.w9_received,
            'reward_percentage': self.reward_percentage,
            'payment_method': self.payment_method,
            'bank_account_number': self.bank_account_number,
            'bank_routing_number': self.bank_routing_number,
            'venmo_handle': self.venmo_handle,
            'id': self.id
            }
