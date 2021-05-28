from sqlalchemy.inspection import inspect


# helpers for converting query result to dict
class Serializer(object):
  def serialize(self):
    return {key: getattr(self, key) for key in inspect(self).attrs.keys()}

  @staticmethod
  def serialize_list(l):
    return [i.serialize() for i in l]
