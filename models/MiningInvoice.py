from sqlalchemy.dialects.postgresql import UUID

from db import db
from models.Assignment import Assignment
from models.mixins.CoreMixin import CoreMixin
from utils.request_utils import Serializer

# host roles
HOST = 'host'
REFERER = 'referer'


class MiningInvoice(CoreMixin, Serializer, db.Model):
  assignment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assignment.id'), nullable=False)
  host_invoice_id = db.Column(UUID(as_uuid=True), db.ForeignKey('host_invoice.id'))
  host_id = db.Column(UUID(as_uuid=True), db.ForeignKey('host.id'), nullable=False)
  host_role = db.Column(db.String(100))
  reward_percentage = db.Column(db.Integer)
  start_date = db.Column(db.DateTime, nullable=False)
  end_date = db.Column(db.DateTime, nullable=False)
  hnt_mined = db.Column(db.Float, nullable=False)
  hnt_owed = db.Column(db.Float, nullable=False)

  host_invoice = db.relationship("HostInvoice", back_populates="mining_invoices")

  def serialize(self):
    assignment = Assignment.query.get(self.assignment_id)
    return {
      'assignment_id': str(self.assignment_id),
      'hotspot_name': assignment.hotspot.name,
      'host_name': "{} {}".format(self.host_invoice.host.first_name, self.host_invoice.host.last_name),
      'host_invoice_id': str(self.host_invoice_id),
      'host_id': str(self.host_id),
      'host_role': self.host_role,
      'reward_percentage': self.reward_percentage,
      'start_date': self.start_date,
      'end_date': self.end_date,
      'hnt_mined': self.hnt_mined,
      'hnt_owed': self.hnt_owed,
    }
