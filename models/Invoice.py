from db import db
from utils.request_utils import Serializer
from models.mixins.CoreMixin import CoreMixin
from sqlalchemy.dialects.postgresql import UUID
from models.Host import Host


class Invoice(CoreMixin, Serializer, db.Model):
  hotspot_name = db.Column(db.String(100), nullable=False)
  hotspot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hotspot.id'), nullable=False)
  host_id = db.Column(UUID(as_uuid=True), db.ForeignKey('host.id'), nullable=False)
  host_last_name = db.Column(db.String(100), nullable=False)
  host_first_name = db.Column(db.String(100), nullable=False)
  host_email = db.Column(db.String(100), nullable=False)
  start_date = db.Column(db.DateTime(timezone=True), nullable=False)
  end_date = db.Column(db.DateTime(timezone=True), nullable=False)
  hnt_amount = db.Column(db.Float, nullable=False)
  paid = db.Column(db.Boolean, default=False, nullable=False)
  paid_from_hnt_wallet = db.Column(db.String(100))
  paid_to_hnt_wallet = db.Column(db.String(100))


  def serialize(self):
    host = Host.query.get(self.host_id).serialize()
    return {'hotspot_name': self.hotspot_name,
            'host': self.host_id,
            'paid': self.paid,
            'hnt_amount': self.hnt_amount,
            'paid_from_hnt_wallet': self.paid_from_hnt_wallet,
            'paid_to_hnt_wallet': self.paid_to_hnt_wallet,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'host_first_name': host['first_name'],
            'host_last_name': host['last_name']
            }
