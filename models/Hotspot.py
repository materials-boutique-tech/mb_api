from db import db
from models.mixins.CoreMixin import CoreMixin
from utils.api_error import FormError
from utils.request_utils import Serializer
from utils.validation_utils import min_length, required_length, type_hotspot_name
from utils.validation_utils import validate


class Hotspot(CoreMixin, Serializer, db.Model):
  net_add = db.Column(db.String(120), unique=True, nullable=False)
  model = db.Column(db.String(120), nullable=False)
  name = db.Column(db.String(100), unique=True, nullable=False)
  assignments = db.relationship('Assignment', backref='hotspot')

  validation = {
    'net_add': [required_length(51)],
    'model': [min_length(3)],
    'name': [type_hotspot_name, min_length(15)],
  }

  def serialize(self):
    return {
      'name': self.name,
      'id': self.id,
      'net_add': self.net_add,
      'model': self.model,
    }

  @staticmethod
  def unassigned():
    query = ('select * from hotspot where hotspot.id not in (select hotspot_id from hotspot inner join '
             '(select *  from assignment where assignment.end_date is null) as hotspots_with_active_assignment '
             'on hotspots_with_active_assignment.hotspot_id = hotspot.id);')
    return db.session.execute(query)

  @staticmethod
  def validate_unique(data):
    if Hotspot.query.filter_by(name=data['name']).first(): return False
    return not Hotspot.query.filter_by(net_add=data['net_add']).first()

  @staticmethod
  def add(data):
    validate(data, Hotspot.validation)

    if not Hotspot.validate_unique(data):
      raise FormError('hotspot with the provided name or net address already exists')

    db.session.add(Hotspot(net_add=data['net_add'],
                           name=data['name'],
                           model=data['model']
                           ))
    db.session.commit()

  @staticmethod
  def update(data):
    validate(data, Hotspot.validation)

    _hotspot = Hotspot.query.get(data['id'])
    _hotspot.name = data['name'].lower(),
    _hotspot.net_add = data['net_add']
    _hotspot.model = data['model']

    db.session.commit()

  @staticmethod
  def all_hotspots():
    return Hotspot.query.all()
