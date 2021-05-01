from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db import db


class CoreMixin(object):
  id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
  archived = db.Column(db.Boolean, default=False, nullable=False)
