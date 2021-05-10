from db import db
from utils.request_utils import Serializer
from models.mixins.CoreMixin import CoreMixin
from sqlalchemy.dialects.postgresql import UUID


class Hotspot(CoreMixin, Serializer, db.Model):
  host_id = db.Column(UUID(as_uuid=True), db.ForeignKey('host.id'))
  net_add = db.Column(db.String(120), unique=True, nullable=False)
  # model = db.Column(db.String(120))
  name = db.Column(db.String(100), unique=True, nullable=False)
  last_transferred = db.Column(db.DateTime)
  invoices = db.relationship('Invoice', backref='hotspot', lazy=True)

  def __repr__(self):
    return 'Hotspot: {}, {}, {}'.format(self.name, self.net_add, self.host.email)

  def serialize(self):
    return {'name': self.name,
            'id': self.id,
            'net_add': self.net_add,
            # 'model': self.model,
            'host_email': self.host.email if self.host else 'none',
            'host_email': self.host.email if self.host else 'none',
            'host_city': self.host.city if self.host else 'none',
            'last_transferred': self.last_transferred if self.last_transferred
            else 'never-transferred'
            }
