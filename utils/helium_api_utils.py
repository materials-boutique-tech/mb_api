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


def start_current_month():
  today = datetime.utcnow()
  _start_cur_month, _ = month_range(today.month, today.year)
  return _start_cur_month


def reward_time_ranges(hs_transfer_date):
  ranges = []
  _start_current_month = start_current_month()

  # generate invoice for each month, ending with the last complete month
  # (no invoice is generated for the current month)
  if hs_transfer_date.month < _start_current_month.month:
    first_bin_start = hs_transfer_date

    _, first_bin_end = month_range(first_bin_start.month, first_bin_start.year)
    ranges.append([first_bin_start, first_bin_end])

    last_bin_end = first_bin_end

    while last_bin_end < _start_current_month:
      start, end = month_range(last_bin_end.month, last_bin_end.year)
      ranges.append([start, end])
      last_bin_end = end

  return ranges


def generate_invoices():
  for host in Host.query.all():
    for hotspot in host.hotspots:
      generate_invoices_for_hotspot(hotspot, host)

def other_rewards_api_call(hotspot, range_start, range_end):
  path = "https://api.helium.io/v1/hotspots/{}/rewards?min_time={}&max_time={}"
  path = path.format(hotspot.net_add, range_start.isoformat(), range_end.isoformat())
  print(path)
  response = requests.get(path)
  cursor = json.loads(response.content)['cursor']
  if cursor:
    response = requests.get(path+'&cursor={}'.format(cursor))
    print("AFTER CURSOR", response)
    total = 0
    json.loads(response.content)['data']
    for x in json.loads(response.content)['data']:
      # print('x looks like',x)
      total+=x['amount']
    # print("{} amount {} for start date {} ".format(hotspot.serialize()['name'], total, range_start))
    return total


def helium_rewards_api_call(hotspot, range_start, range_end):
  path = "https://api.helium.io/v1/hotspots/{}/rewards/sum?min_time={}&max_time={}"
  path = path.format(hotspot.net_add, range_start.isoformat(), range_end.isoformat())
  # print("the path", path)
  response = requests.get(path)
  return json.loads(response.content)


def generate_invoices_for_hotspot(hotspot, host):
  rewards_start_date = hotspot.serialize()['last_transferred']
  ranges = reward_time_ranges(rewards_start_date)

  for r in ranges:
    create_invoice(hotspot, host, r[0], r[1])
    # print("the total for {}".format(r[0].strftime("%m/%d/%Y, %H:%M:%S"),r[1].strftime("%m/%d/%Y, %H:%M:%S")))


def create_invoice(hotspot, host, start_date, end_date):
  hotspot_id = hotspot.serialize()['id']

  # make sure an invoice does not exist for the same hotspot in the same period
  if Invoice.query.filter_by(hotspot_id=hotspot_id, start_date=start_date).first():
      return
  other_rewards_api_call(hotspot, start_date, end_date)
  response = helium_rewards_api_call(hotspot, start_date, end_date)
  hnt_mined_in_range = response['data']['total']
  hnt_owed = hnt_mined_in_range * (host.reward_percentage/100)

  db.session.add(
    Invoice(hotspot_id=hotspot_id,
            host_id=host.serialize()['id'],
            start_date=start_date,
            end_date=end_date,
            hnt_mined=hnt_mined_in_range,
            hnt_owed=hnt_owed,
            host_reward_percentage=host.reward_percentage # record this as it could change in the future
            ))

  db.session.commit()
