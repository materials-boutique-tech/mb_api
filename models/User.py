from db import db
from utils.request_utils import Serializer
from flask_login import UserMixin
from models.mixins.CoreMixin import CoreMixin


class User(UserMixin, CoreMixin, Serializer, db.Model):
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(100), nullable=False)
  first_name = db.Column(db.String(80), nullable=False)
  last_name = db.Column(db.String(120), nullable=False)

  def __repr__(self):
    return 'User: {}, {}, {}'.format(self.last_name, self.first_name, self.email)
