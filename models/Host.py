from db import db
from utils.request_utils import Serializer
from models.mixins.CoreMixin import CoreMixin


class Host(db.Model, CoreMixin, Serializer):
  first_name = db.Column(db.String(80), nullable=False)
  last_name = db.Column(db.String(120), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  street = db.Column(db.String(120), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  zip = db.Column(db.String(120), nullable=False)
  hnt_wallet = db.Column(db.String(120))
  w9_received = db.Column(db.Boolean, server_default='false', nullable=False)
  reward_percentage = db.Column(db.Integer, server_default='50', nullable=False)
  hotspots = db.relationship('Hotspot', backref='host', lazy=True)
  invoices = db.relationship('Invoice', backref='host', lazy=True)
  # contract_version = db.Column(db.String(120), nullable=False, default="1.0.0")


  def __repr__(self):
    # TODO make this generic across models
    return 'Host: {}'.format(self.id)

  def serialize(self):
    return {'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'hnt_wallet':self.hnt_wallet,
            'hotspots': Serializer.serialize_list(self.hotspots),
            'hotspot_count': len(self.hotspots),
            'w9_received':self.w9_received,
            'reward_percentage':self.reward_percentage,
            'id': self.id
            }
