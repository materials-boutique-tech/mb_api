from flask import Response
from sqlalchemy.inspection import inspect


# helpers for converting query result to dict
class Serializer(object):
  def serialize(self):
    return {key: getattr(self, key) for key in inspect(self).attrs.keys()}

  @staticmethod
  def serialize_list(l):
    return [i.serialize() for i in l]


# http error handlers
def not_authorized_401(e):
  return Response('not authorized', status=401, mimetype='application/json')


def already_exist_error(table_name, field_name):
  return Response('{} with the provided {} already exists'.format(table_name, field_name), status=400,
                  mimetype='application/json')


def form_submission_error(error_msg):
  return Response('Form error: {}'.format(error_msg), status=422, mimetype='application/json')
