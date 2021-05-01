from dateutil.relativedelta import relativedelta
from datetime import datetime, date, time
from models.Host import Host
from models.Invoice import Invoice
import requests
import json
from db import db


def start_day(_date):
  return datetime.combine(_date, time.min)


# given a month and year returns an array like:
# [<beginning_month_datetime>, <beginning_following_month_datetime>]
def month_range(month, year):
  start = date(year, month, 1)
  end = start + relativedelta(months=1)
  return [start, end]


def reward_time_ranges(start_date):
  ranges = []

  # start of first bin is the last_transferred_date for the hotspot
  first_bin_start = start_date
  _, first_bin_end = month_range(first_bin_start.month, first_bin_start.year)
  ranges.append([first_bin_start, first_bin_end])

  today = datetime.now()
  start_current_month, _ = month_range(today.month, today.year)
  last_bin_end = first_bin_end

  while last_bin_end < start_current_month:
    start, end = month_range(last_bin_end.month, last_bin_end.year)
    ranges.append([start, end])
    last_bin_end = end

  return ranges


def generate_invoices():
  for host in Host.query.all():
    for hotspot in host.hotspots:
      generate_invoices_for_hotspot(hotspot, host)


def helium_rewards_api_call(hotspot, range_start, range_end):
  path = "https://api.helium.io/v1/hotspots/{}/rewards/sum?min_time={}&max_time={}"
  path = path.format(hotspot.net_add, range_start.isoformat(), range_end.isoformat())
  response = requests.get(path)
  return json.loads(response.content)


# TODO: check that invoice doesn't exist for hotspot/start-date before creating one
def generate_invoices_for_hotspot(hotspot, host):
  rewards_start_date = hotspot.serialize()['last_transferred']
  ranges = reward_time_ranges(rewards_start_date)
  print('\n\n the ranges look like')
  for r in ranges:
    response = helium_rewards_api_call(hotspot, r[0], r[1])
    hnt_mined_in_range = response['data']['total']
    if hnt_mined_in_range > 0:
      create_invoice(hotspot, host, r[0], r[1], hnt_mined_in_range)

    print("the total for {}".format(r[0].strftime("%m/%Y")), hnt_mined_in_range)


def create_invoice(hotspot, host, start_date, end_date, hnt_amount):
  hotspot_id = hotspot.serialize()['id']
  hotspot_name = hotspot.serialize()['name']

  if Invoice.query.filter_by(hotspot_id=hotspot_id, start_date=start_date).first():
      return

  db.session.add(
    Invoice(hotspot_id=hotspot_id,
            hotspot_name=hotspot_name,
            host_id=host.serialize()['id'],
            host_first_name=host.serialize()['first_name'],
            host_last_name=host.serialize()['last_name'],
            host_email=host.serialize()['email'],
            start_date=start_date,
            end_date=end_date,
            hnt_amount=hnt_amount
            ))
  db.session.commit()
