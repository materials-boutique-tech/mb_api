from sqlalchemy.dialects.postgresql import UUID

from db import db
from models.mixins.CoreMixin import CoreMixin
from utils.request_utils import Serializer


class HostInvoice(CoreMixin, Serializer, db.Model):
  host_id = db.Column(UUID(as_uuid=True), db.ForeignKey('host.id'))
  start_date = db.Column(db.DateTime, nullable=False)
  end_date = db.Column(db.DateTime, nullable=False)
  hnt_owed = db.Column(db.Float, nullable=False)
  paid = db.Column(db.Boolean, default=False, nullable=False)
  paid_at = db.Column(db.DateTime)
  payment_method = db.Column(db.String(100))
  paid_from_hnt_wallet = db.Column(db.String(100))
  paid_to_hnt_wallet = db.Column(db.String(100))
  paid_to_bank_details = db.Column(db.String(100))  # accountNum_routingNum
  paid_to_venmo_handle = db.Column(db.String(100))

  mining_invoices = db.relationship('MiningInvoice')

  def serialize(self):
    return {
      'id': self.id,
      'host_id': self.host_id,
      'host_name': "{} {}".format(self.host.first_name, self.host.last_name),
      'start_date': self.start_date,
      'end_date': self.end_date,
      'hnt_owed': self.hnt_owed,
      'paid': self.paid,
      'paid_at': self.paid_at,
      'payment_method': self.payment_method,
      'paid_from_hnt_wallet': self.paid_from_hnt_wallet,
      'paid_to_hnt_wallet': self.paid_to_hnt_wallet,
      'paid_to_bank_details': self.paid_to_bank_details,
      'paid_to_venmo_handle': self.paid_to_venmo_handle,
      'mining_invoices': [m.serialize() for m in self.mining_invoices],
    }

  @staticmethod
  def by_id(host_invoice_id):
    return HostInvoice.query.get(host_invoice_id)

  @staticmethod
  def by_host(host_id):
    return HostInvoice.query.filter_by(host_id=host_id).all()
