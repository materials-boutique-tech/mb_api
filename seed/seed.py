from werkzeug.security import generate_password_hash

from db import db
from models.Host import Host
from models.Hotspot import Hotspot
from models.User import User


def seed_users():
  users = [{'email': 'rl', 'password': 'rl1', 'first_name': 'Reese',
            'last_name': 'Smith'},
           {'email': 'saul_???', 'password': 'saul_???!!!???', 'first_name': 'Saul',
            'last_name': 'Smith'},
           {'email': 'martin_???', 'password': 'martin_???!!!???',
            'first_name': 'Martin', 'last_name': 'Smith'}]
  for user in users:
    existing = User.query.filter_by(email=user['email']).first()

    if not existing:
      # noinspection PyArgumentList
      new_user = User(email=user['email'], first_name=user['first_name'], last_name=user['last_name'],
                      password=generate_password_hash(user['password'], method='sha256'))
      db.session.make_new(new_user)
      db.session.commit()


def seed_hosts():
  hosts = [
    {"id": 16, "zip": "3220-435", "first_name": "Derk", "last_name": "Willows", "email": "dwillowsf@cisco.com",
     "phone": "959-875-7380",
     "street": "841 Calypso Plaza", "city": "Golubinci", "state": "Coimbra",
     "hnt_wallet": "12n53rX6m2om5AbLswmyHwBPJY57B3wbHh", 'payment_method': 'hnt'},
    {"id": 17, "first_name": "Neala", "last_name": "Connerly", "email": "nconnerlyg@sourceforge.net",
     "phone": "305-540-6836", "street": "11518 Elka Street", "city": "Senhor da Serra", "state": "Coimbra",
     "zip": "3220-435", "hnt_wallet": "1B7nt1gZVgwDfbuFtQf2TQzdgLnB85SJWU", 'payment_method': 'hnt'},
    {"id": 18, "first_name": "Jesse", "last_name": "Trethewey", "email": "jtretheweyh@ycombinator.com",
     "phone": "305-697-7276", "street": "562 Eagle Crest Road", "city": "Tours", "state": "Centre",
     "zip": "37942 CEDEX 9", "hnt_wallet": "1K2nsKLh4GwJppJ85xeauyJgH88sN74cuH", 'payment_method': 'hnt'},
    {"id": 19, "first_name": "Con", "last_name": "Fawley", "email": "cfawleyi@jalbum.net", "phone": "567-201-1990",
     "street": "92339 Vahlen Parkway", "city": "Loivos", "state": "Vila Real", "zip": "5425-055",
     "hnt_wallet": "15EyHpBCCRaZKP1c4qhvwn6WYL1eDz8Hr2", 'payment_method': 'hnt'},
    {"id": 20, "first_name": "Dex", "last_name": "Sterricker", "email": "dsterrickerj@gov.uk", "phone": "530-636-0962",
     "street": "7 Mcbride Parkway", "city": "Koffiefontein", "zip": "9987", "state": "Coimbra",
     "hnt_wallet": "1MKqcU4yiEzSueWdGkGSyPuEcCsBHT9T17", 'payment_method': 'fiat'}]

  for host in hosts:
    existing = Host.query.filter_by(email=host['email']).first()

    if not existing:
      # noinspection PyArgumentList
      db.session.make_new(Host(
        email=host['email'],
        first_name=host['first_name'],
        last_name=host['last_name'],
        phone=host['phone'],
        street=host['street'],
        city=host['city'],
        state=host['state'],
        zip=host['zip'],
        hnt_wallet=host['hnt_wallet'],
        payment_method=host['payment_method']
      ))
      db.session.commit()


def seed_hotspots():
  hotspots = [
    {'net_add': "11sDK9KUao8SudAgzRzKHQT5JjvKdG7v9bUzpu6LEb85DyYuMrg", 'name': "magic_shadow_tiger", 'model': "rak"},
    {'net_add': "11fieGXr67sevi4PQKimfjBkyVLa3JgQBmiiKebqE2hVszNdXuB", 'name': "proper_mustard_yeti", 'model': "rak"},
    {'net_add': "112UgNkWKUzLEW9cdYAE9AdYmfQDSUJeJZdDQsLN6aA1x7byV7eh", 'name': "fluffy_glass_meerkat", 'model': "rak"},
    {'net_add': "11Jd6xUVS3ztkYYjv29Q1bu8c1RmMGedAqXAmt71fDn8ah3Zkd7", 'name': "attractive_peanut_lark",
     'model': "rak"},
  ]

  for hotspot in hotspots:
    existing = Hotspot.query.filter_by(net_add=hotspot['net_add']).first()

    if not existing:
      # noinspection PyArgumentList
      db.session.make_new(Hotspot(
        net_add=hotspot['net_add'],
        name=hotspot['name'],
        model=hotspot['model'],
      ))
      db.session.commit()


def seed_all():
  seed_users()
  seed_hosts()
  seed_hotspots()
