import json
from datetime import datetime, date, time

import requests
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_

from db import db
from models.Assignment import Assignment
from models.Host import Host
from models.HostInvoice import HostInvoice
from models.MiningInvoice import MiningInvoice


def generate_invoices_job(app):
  def job():
    with app.app_context():
      generate_invoices()

  return job


def generate_invoices():
  delete_mining_invoices()
  delete_unpaid_host_invoices()
  generate_mining_invoices()
  generate_host_invoices()


START_INVOICE_TS = Assignment.format_date('01/01/21')


def delete_unpaid_host_invoices():
  HostInvoice.query.filter(HostInvoice.paid.isnot(True)).delete()


def delete_mining_invoices():
  MiningInvoice.query.delete()


def generate_host_invoices():
  ranges = date_ranges(START_INVOICE_TS, start_day(start_current_month()))
  for host in Host.query.all():
    for r in ranges:
      generate_host_invoice(host, r)


def calc_hnt_owed(mining_invoices):
  return sum(m.hnt_owed for m in mining_invoices)


def generate_host_invoice(host, date_range):
  start, end = date_range

  mining_host_invoices_in_range = MiningInvoice.query.filter(
    and_(MiningInvoice.host_id == host.id,
         MiningInvoice.start_date >= start,
         MiningInvoice.end_date <= end)).all()

  if len(mining_host_invoices_in_range):
    hnt_owed = calc_hnt_owed(mining_host_invoices_in_range)

    invoice = HostInvoice(
      host_id=host.id,
      start_date=start,
      end_date=end,
      hnt_owed=hnt_owed,
      mining_invoices=mining_host_invoices_in_range,
    )

    db.session.add(invoice)
    db.session.commit()


def generate_mining_invoices():
  for assignment in Assignment.query.all():
    invoices_for_assignment(assignment)


def invoices_for_assignment(assignment):
  end_invoice_range = assignment.end_date or start_day(start_current_month())

  for start, end in date_ranges(assignment.start_date, end_invoice_range):
    create_mining_invoice(assignment, start, end)


def create_mining_invoice(assignment, start_date, end_date):
  hnt_mined_in_range = helium_rewards_api_call(assignment, start_date, end_date)
  helium_api_call_v2(assignment, start_date, end_date)

  def make_invoice(host_role, reward_percentage):
    return MiningInvoice(
      assignment_id=assignment.id,
      host_id=assignment.host_id if host_role == 'host' else assignment.referer_id,
      host_role=host_role,
      start_date=start_date,
      end_date=end_date,
      hnt_mined=hnt_mined_in_range,
      hnt_owed=hnt_mined_in_range * (reward_percentage / 100),
      reward_percentage=assignment.host_reward_percentage  # record this as it could change in the future
    )

  db.session.add(make_invoice('host', assignment.host_reward_percentage))

  if assignment.referer_id:
    if assignment.mb_termination_aggressor is not False:
      db.session.add(make_invoice('referer', assignment.referer_reward_percentage))

  db.session.commit()


def helium_rewards_api_call(assignment, range_start, range_end):
  path = "https://api.helium.io/v1/hotspots/{}/rewards/sum?min_time={}&max_time={}"
  path = path.format(assignment.hotspot.net_add, range_start.isoformat(), range_end.isoformat())
  response = requests.get(path)
  return json.loads(response.content)['data']['total']


def helium_api_call_v2(assignment, range_start, range_end):
  _path = "https://api.helium.io/v1/hotspots/{}/rewards?min_time={}&max_time={}"
  _path = _path.format(assignment.hotspot.net_add, range_start.isoformat(), range_end.isoformat())

  res = []

  cursor = 'unset'

  while cursor:
    path = _path

    if cursor and (cursor != 'unset'):
      path += '&cursor={}'.format(cursor)

    response = requests.get(path)
    content = json.loads(response.content)
    res.extend(content['data'])

    cursor = 'cursor' in content

    if cursor:
      cursor = content['cursor']

  total = 0

  for record in res:
    total += record['amount']

  return total/100000000


def start_day(_date):
  return datetime.combine(_date, time.min)


# given a month and year returns an array like:
# [<beginning_month_datetime>, <beginning_following_month_datetime>]
def month_range(month, year):
  start = date(year, month, 1)
  end = start + relativedelta(months=1)
  return [start, end]


def start_current_month():
  today = datetime.utcnow()
  _start_cur_month, _ = month_range(today.month, today.year)
  return _start_cur_month


# pass end date for terminated assignments, otherwise we stop at end of last complete month
def date_ranges(start_date, end_date):
  # if the assignment starts and ends in the same month&year
  if end_date and (start_date.month == end_date.month and start_date.year == end_date.year):
    return [[start_date, end_date]]

  ranges = []

  _, first_bin_end = month_range(start_date.month, start_date.year)
  ranges.append([start_date, first_bin_end])

  last_bin_end = first_bin_end

  while start_day(last_bin_end) < end_date:
    start, end = month_range(last_bin_end.month, last_bin_end.year)
    end = end_date if end_date < start_day(end) else end
    ranges.append([start, end])
    last_bin_end = end

  return ranges
