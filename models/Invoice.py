from sqlalchemy.dialects.postgresql import UUID
from db import db
from models.Host import Host
from models.Hotspot import Hotspot
from models.mixins.CoreMixin import CoreMixin
from utils.request_utils import Serializer


class Invoice(CoreMixin, Serializer, db.Model):
  hotspot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hotspot.id'), nullable=False)
  host_id = db.Column(UUID(as_uuid=True), db.ForeignKey('host.id'), nullable=False)
  start_date = db.Column(db.DateTime, nullable=False)
  end_date = db.Column(db.DateTime, nullable=False)
  hnt_mined = db.Column(db.Float, nullable=False)
  hnt_owed = db.Column(db.Float, nullable=False)
  host_reward_percentage = db.Column(db.Integer, nullable=False)
  paid = db.Column(db.Boolean, default=False, nullable=False)
  paid_at = db.Column(db.DateTime)
  payment_method = db.Column(db.String(100))
  paid_from_hnt_wallet = db.Column(db.String(100))
  paid_to_hnt_wallet = db.Column(db.String(100))

  def serialize(self):
    host = Host.query.get(self.host_id).serialize()
    hotspot = Hotspot.query.get(self.hotspot_id).serialize()

    return {'host_id': self.host_id,
            'hotspot_name': hotspot['name'],
            'host_first_name': host['first_name'],
            'host_last_name': host['last_name'],
            'host_reward_percentage': host['reward_percentage'],
            'start_date': self.start_date,
            'end_date': self.end_date,
            'paid': self.paid,
            'paid_from_hnt_wallet': self.paid_from_hnt_wallet,
            'paid_to_hnt_wallet': self.paid_to_hnt_wallet,
            'hnt_mined': self.hnt_mined,
            'hnt_owed': self.hnt_owed,
            }
