from sqlalchemy.inspection import inspect
from flask import Response


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
