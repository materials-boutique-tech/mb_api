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
  hotspots = db.relationship('Hotspot', backref='host', lazy=True)
  invoices = db.relationship('Invoice', backref='host', lazy=True)

  def __repr__(self):
    return 'Host: {}, {}, {}'.format(self.last_name, self.first_name, self.email)

  def serialize(self):
    return {'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'state': self.state,
            'street': self.street,
            'phone': self.phone,
            'city': self.city,
            'hotspots': Serializer.serialize_list(self.hotspots),
            'id': self.id};
