import datetime

from sqlalchemy.dialects.postgresql import UUID

from db import db
from models.Hotspot import Hotspot
from models.mixins.CoreMixin import CoreMixin
from utils.api_error import FormError
from utils.request_utils import Serializer
from utils.validation_utils import validate, number_in_range, required_length, type_bool, date_string_format


class Assignment(db.Model, CoreMixin, Serializer):
  start_date = db.Column(db.DateTime, nullable=False)
  end_date = db.Column(db.DateTime)
  mb_termination_aggressor = db.Column(db.Boolean)
  host_reward_percentage = db.Column(db.Integer, server_default='50', nullable=False)
  referer_reward_percentage = db.Column(db.Integer, server_default='5')
  supplement_received = db.Column(db.Boolean, server_default='false', nullable=False)

  host_id = db.Column(UUID(as_uuid=True), db.ForeignKey('host.id'), nullable=False)
  hotspot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hotspot.id'), nullable=False)
  referer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('host.id'))

  def serialize(self):
    return {
      'start_date': self.start_date,
      'end_date': self.end_date,
      'mb_termination_aggressor': self.mb_termination_aggressor,
      'host_reward_percentage': self.host_reward_percentage,
      'referer_reward_percentage': self.referer_reward_percentage,
      'supplement_received': self.supplement_received,
      'id': self.id,
    }

  validation = {
    'host_id': [required_length(36)],
    'referer_id': [required_length(36)],
    'hotspot_id': [required_length(36)],
    'start_date': [date_string_format],
    'end_date': [date_string_format],
    'referer_reward_percentage': [number_in_range(1, 100)],
    'host_reward_percentage': [number_in_range(1, 100)],
    'mb_termination_aggressor': [type_bool],
    'supplement_received': [type_bool],
  }

  @staticmethod
  def all_assignments():
    # noinspection SqlResolve
    query = ('select assignment.id as assignment_id, * from assignment '
             'inner join hotspot on assignment.hotspot_id = hotspot.id '
             'inner join host on assignment.host_id = host.id;')
    return db.session.execute(query).all()

  @staticmethod
  def get_assignment(a_id):
    return Assignment.query.get(a_id).serialize()

  @staticmethod
  def add(data):
    validate(data, Assignment.validation)
    hotspot = Hotspot.query.get(data['hotspot_id'])
    start_date = Assignment.format_date(data['start_date'])
    Assignment.validate_start_date(hotspot, start_date)

    # noinspection PyArgumentList
    new_assignment = Assignment(start_date=data['start_date'],
                                host_reward_percentage=data['host_reward_percentage'],
                                host_id=data['host_id'],
                                hotspot_id=data['hotspot_id'])

    # optional fields
    if 'referer_id' in data:
      if data['referer_id'] == data['host_id']:
        raise FormError('host and referer cannot be the same person')
      new_assignment.referer_id = data['referer_id']

    if 'referer_reward_percentage' in data:
      new_assignment.referer_reward_percentage = data['referer_reward_percentage']

    if 'supplement_received' in data:
      new_assignment.supplement_received = data['supplement_received']

    db.session.make_new(new_assignment)
    db.session.commit()

  @staticmethod
  def terminate(data):
    validate(data, Assignment.validation)
    assignment = Assignment.query.get(data['id'])

    if not assignment: raise FormError('assignment could not be found with the provided id')

    Assignment.validate_end_date(assignment.hotspot, assignment.start_date, data['end_date'])
    assignment.end_date = data['end_date']

    if 'mb_termination_aggressor' in data:
      assignment.mb_termination_aggressor = data['mb_termination_aggressor']
    else:
      assignment.mb_termination_aggressor = False
    db.session.commit()
    return True

  @staticmethod
  def active_assignment_for_hotspot(hotspot_id):
    return Assignment.query.filter_by(end_date=None, hotspot_id=hotspot_id).first()

  @staticmethod
  def terminated_assignment_for_hotspot(hotspot_id):
    # noinspection PyUnresolvedReferences
    return Assignment.query.filter(Assignment.end_date.isnot(None),
                                   Assignment.hotspot_id == hotspot_id).all()

  @staticmethod
  def format_date(date):
    return datetime.datetime.strptime(date, "%m/%d/%y")

  @staticmethod
  def validate_start_date(hotspot, start_date):
    if Assignment.active_assignment_for_hotspot(hotspot.id):
      raise FormError("hotspot has an active assignment")
    Assignment.validate_against_existing_assignments(hotspot, start_date)

  @staticmethod
  def validate_end_date(hotspot, start_date, end_date):
    now = datetime.datetime.utcnow()
    end_date = Assignment.format_date(end_date)

    if end_date > now:
      raise FormError("end date cannot be after today's date".format(end_date, start_date))
    if end_date < start_date:
      raise FormError("provided end date {} is before the assignment start date {}".format(end_date, start_date))
    Assignment.validate_against_existing_assignments(hotspot, end_date)

  @staticmethod
  def validate_against_existing_assignments(hotspot, date):
    for a in Assignment.terminated_assignment_for_hotspot(hotspot.id):
      if date == a.start_date or date == a.end_date:
        raise FormError("start date is the same as the start or end date of an existing assignment")
      if a.start_date < date < a.end_date:
        raise FormError("start date falls between start and end date of an existing assignment")
