from sqlalchemy.dialects.postgresql import UUID
from db import db
from models.mixins.CoreMixin import CoreMixin
from utils.request_utils import Serializer


class Hotspot(CoreMixin, Serializer, db.Model):
  host_id = db.Column(UUID(as_uuid=True), db.ForeignKey('host.id'))
  net_add = db.Column(db.String(120), unique=True, nullable=False)
  model = db.Column(db.String(120), nullable=False)
  name = db.Column(db.String(100), unique=True, nullable=False)
  last_transferred = db.Column(db.DateTime)
  invoices = db.relationship('Invoice', backref='hotspot', lazy=True)

  def serialize(self):
    return {'name': self.name,
            'id': self.id,
            'net_add': self.net_add,
            'model': self.model,
            'host_email': self.host.email if self.host else 'none',
            'host_email': self.host.email if self.host else 'none',
            'host_city': self.host.city if self.host else 'none',
            'last_transferred': self.last_transferred
            }
