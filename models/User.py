from flask_login import UserMixin

from db import db
from models.mixins.CoreMixin import CoreMixin
from utils.request_utils import Serializer


class User(UserMixin, CoreMixin, Serializer, db.Model):
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(100), nullable=False)
  first_name = db.Column(db.String(80), nullable=False)
  last_name = db.Column(db.String(120), nullable=False)
