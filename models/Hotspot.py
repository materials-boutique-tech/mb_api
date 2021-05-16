import datetime

from sqlalchemy.dialects.postgresql import UUID

from db import db
from models.mixins.CoreMixin import CoreMixin
from utils.request_utils import Serializer
from utils.validation_utils import min_length, required_length, date_string_format, type_string, type_hotspot_name


class Hotspot(CoreMixin, Serializer, db.Model):
  host_id = db.Column(UUID(as_uuid=True), db.ForeignKey('host.id'))
  net_add = db.Column(db.String(120), unique=True, nullable=False)
  model = db.Column(db.String(120), nullable=False)
  name = db.Column(db.String(100), unique=True, nullable=False)
  last_transferred = db.Column(db.DateTime)
  invoices = db.relationship('Invoice', backref='hotspot', lazy=True)

  validation = {
    'net_add': [required_length(51), type_string],
    'model': [min_length(3), type_string],
    'name': [type_hotspot_name, min_length(15), type_string],
    'last_transferred': [date_string_format, type_string],
  }

  def serialize(self):
    return {'name': self.name,
            'id': self.id,
            'net_add': self.net_add,
            'model': self.model,
            'host_email': self.host.email if self.host else 'none',
            'host_city': self.host.city if self.host else 'none',
            'last_transferred': self.last_transferred
            }
