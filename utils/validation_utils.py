import re

from utils.api_error import FormError


# validators used in model CRUD methods
def validate(data, validation):
  errors = []

  for field_name in validation:
    field_validation = validation[field_name]
    if (not field_name in data) or (data[field_name] is None): continue

    for validator in field_validation:
      err_msg = validator(field_name, data)
      if err_msg: errors.append(err_msg)

  if len(errors): raise FormError(', '.join(errors))


def min_length(min_len):
  def ml(field_name, data):
    if len(data[field_name]) < min_len: return '{} has a minimum length of {}'.format(field_name, min_len)

  return ml


def max_length(max_len):
  def ml(field_name, data):
    if len(data[field_name]) > max_len: return '{} has a maximum length of {}'.format(field_name, max_len)

  return ml


def number_in_range(_min, _max):
  def nir(field_name, data):
    # noinspection PyBroadException
    try:
      int(data[field_name])
    except:
      return '{} is not a number'.format(field_name)

    val = int(data[field_name])
    if (val < _min) or (val > _max): return '{} must be between {} and {}'.format(field_name, _min, _max)

  return nir


def required_length(required_len):
  def rl(field_name, data):
    if len(data[field_name]) != required_len:
      return '{} must be {} characters in length'.format(field_name, required_len)

  return rl


def one_of(allowed_list):
  def func(field_name, data):
    if not data[field_name] in allowed_list:
      return "{} must be one of: {}".format(field_name, ', '.join(allowed_list))

  return func


def type_number(field_name, data):
  if type(data[field_name]) != int:
    return "{} should be a number".format(field_name)


def type_string(field_name, data):
  if type(data[field_name]) != str:
    return "{} should be a string".format(field_name)


def type_bool(field_name, data):
  if type(data[field_name]) != bool:
    return "{} should be a bool".format(field_name)


def date_string_format(field_name, data):
  if not re.fullmatch('^\d{2}/\d{2}/\d{2}', data[field_name]):
    return "{} should have format mm/dd/yy".format(field_name)


def type_name(field_name, data):
  if not re.fullmatch('^[a-zA-Z\s]+$', data[field_name]):
    return "{} can only contain letters and spaces".format(field_name)


def type_email(field_name, data):
  if not re.fullmatch('^(\w|\.|_|-)+[@](\w|_|-|\.)+[.]\w{2,3}$', data[field_name]):
    return "{} invalid".format(field_name)


def type_phone(field_name, data):
  if not re.search('^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$',
                   data[field_name]):
    return "{} invalid".format(field_name)


def type_city_or_state(field_name, data):
  if not re.fullmatch('^[a-zA-Z]+(?:[\s-][a-zA-Z]+)*$', data[field_name]):
    return "{} invalid".format(field_name)


def type_zip_code(field_name, data):
  if not re.fullmatch('^(\d{5})([- ])?(\d{4})?', data[field_name]):
    return "{} invalid".format(field_name)


def type_hotspot_name(field_name, data):
  if not re.fullmatch('^[a-z_]*$', data[field_name]):
    return "{} invalid - should contain only lowercase letters and underscore".format(field_name)
  if not len(re.findall('_', data[field_name])) == 2:
    return "{} invalid - should contain three words separated by underscores".format(field_name)
