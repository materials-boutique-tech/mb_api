import datetime

from sqlalchemy.dialects.postgresql import UUID

from db import db
from models.Host import Host
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
  referer_reward_percentage = db.Column(db.Integer)
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

  def is_active(self):
    return self.end_date is None

  @staticmethod
  def all_assignments():
    # noinspection SqlResolve
    query = ('select assignment.id as assignment_id, * from assignment '
             'inner join hotspot on assignment.hotspot_id = hotspot.id '
             'inner join host on assignment.host_id = host.id;')
    return db.session.execute(query).all()

  @staticmethod
  def get_assignment(a_id):
    a = Assignment.query.get(a_id)
    res = a.serialize()

    res['hotspot_name'] = a.hotspot.name
    res['hotspot_id'] = a.hotspot.id

    res['host_label'] = "{} {} ({})".format(a.host.first_name, a.host.last_name, a.host.email)
    res['host_id'] = a.host.id

    if a.referer:
      res['referer_label'] = "{} {} ({})".format(a.referer.first_name, a.referer.last_name, a.referer.email)
      res['referer_id'] = a.referer.id
    return res

  @staticmethod
  def add(data):
    validate(data, Assignment.validation)
    Assignment.validate_dates(data)

    # noinspection PyArgumentList
    new_assignment = Assignment(start_date=data['start_date'],
                                host_reward_percentage=data['host_reward_percentage'],
                                host_id=data['host_id'],
                                hotspot_id=data['hotspot_id'])

    new_assignment.set_optional_fields(data)

    db.session.add(new_assignment)
    db.session.commit()

  @staticmethod
  def update(data):
    assignment = Assignment.query.get(data['id'])

    validate(data, Assignment.validation)
    Assignment.validate_dates(data)

    # noinspection PyArgumentList
    assignment.start_date = data['start_date']
    assignment.host_reward_percentage = data['host_reward_percentage']
    assignment.host_id = data['host_id'],
    assignment.hotspot_id = data['hotspot_id']

    assignment.set_optional_fields(data)

    db.session.commit()

  def set_optional_fields(self, data):
    if 'referer_id' in data:
      if data['referer_id'] == data['host_id']:
        raise FormError('host and referer cannot be the same person')
      self.referer_id = data['referer_id']

      if not 'referer_reward_percentage' in data:
        raise FormError('referer reward percentage is required')

      assignment_id = data['id'] if 'id' in data else None
      if not Host.query.get(data['host_id']).eligible_to_be_referred(assignment_id):
        raise FormError('a referer can only be assigned to a new host')

      self.referer_reward_percentage = data['referer_reward_percentage']

    if 'supplement_received' in data:
      self.supplement_received = data['supplement_received']

    if 'mb_termination_aggressor' in data and not 'end_date' in data:
      raise FormError('cannot set termination aggressor without end date')

    if 'end_date' in data:
      self.end_date = data['end_date']
      if 'mb_termination_aggressor' in data:
        self.mb_termination_aggressor = data['mb_termination_aggressor']

  @staticmethod
  def active_assignment_for_hotspot(hotspot_id):
    return Assignment.query.filter_by(end_date=None, hotspot_id=hotspot_id).first()

  @staticmethod
  def terminated_assignments_for_hotspot(hotspot_id):
    # noinspection PyUnresolvedReferences
    return Assignment.query.filter(Assignment.end_date.isnot(None),
                                   Assignment.hotspot_id == hotspot_id).all()

  @staticmethod
  def format_date(date):
    return datetime.datetime.strptime(date, "%m/%d/%y")

  @staticmethod
  def validate_dates(data):
    start_date = Assignment.format_date(data['start_date'])
    end_date = None

    if 'end_date' in data:
      end_date = Assignment.format_date(data['end_date'])
      if end_date < start_date: raise FormError('assignment end date cannot be before the start date')

    hotspot = Hotspot.query.get(data['hotspot_id'])
    assignment_being_edited = data['id'] if 'id' in data else None

    Assignment.validate_against_existing_assignments(hotspot, start_date, end_date, assignment_being_edited)

  @staticmethod
  def validate_against_existing_assignments(hotspot, start_date, end_date, assignment_being_edited_id):
    active_assignment = Assignment.active_assignment_for_hotspot(hotspot.id)

    if active_assignment:
      active_assignment_being_edited = str(assignment_being_edited_id) == str(active_assignment.id)

      if not active_assignment_being_edited:
        if not end_date: raise FormError('hotspot already has an active assignment - you must provide an end date')
        if start_date > active_assignment.start_date or end_date > active_assignment.start_date:
          raise FormError('start or end date are past the active assignment start date')

    for date in [start_date, end_date]:
      if date:
        for a in Assignment.terminated_assignments_for_hotspot(hotspot.id):
          if str(a.id) != str(assignment_being_edited_id):  # when editing don't compare against self
            if date == a.start_date or date == a.end_date:
              raise FormError("start or end date is the same as start or end date of an existing assignment")
            if a.start_date < date < a.end_date:
              raise FormError("start or end date falls between start and end date of an existing assignment")
            if end_date:
              if start_date < a.start_date and end_date > a.end_date:
                raise FormError("start and end date fully an overlap existing assignment")
