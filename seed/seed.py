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
      db.session.add(new_user)
      db.session.commit()


def seed_hosts():
  hosts = [
    {
      "zip": "22333",
      "first_name": "Derk",
      "last_name": "Willows",
      "email": "dwillowsf@cisco.com",
      "phone": "6662228888",
      "street": "841 Calypso Plaza",
      "city": "Golubinci",
      "state": "Texas",
      "hnt_wallet": "11sDK9KUao8SudAgzRzKHQT5JjvKdG7v9bUzpu6LEb85DyYuMrg",
      'payment_method': 'hnt'
    },
    {
      "zip": "11222",
      "first_name": "Jane",
      "last_name": "Austin",
      "email": "jaus@foo.com",
      "phone": "3339991111",
      "street": "10 Pine",
      "city": "Boston",
      "state": "Wyoming",
      "hnt_wallet": "33sDK9KUao8SudAgzRzKHQT5JjvKdG7v9bUzpu6LEb85DyYuMrg",
      'payment_method': 'fiat'
    },
    {
      "zip": "11222",
      "first_name": "Bill",
      "last_name": "Collins",
      "email": "b@col.com",
      "phone": "1110002222",
      "street": "10 Pine",
      "city": "New York",
      "state": "Delaware",
      "hnt_wallet": "33sDK9KUao8SudAgzRzKHQT5JjvKdG7v9bUzpu6LEb85DyYuMrg",
      'payment_method': 'bank_account'
    },
  ]

  for host in hosts:
    existing = Host.query.filter_by(email=host['email']).first()

    if not existing:
      # noinspection PyArgumentList
      db.session.add(Host(
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
      db.session.add(Hotspot(
        net_add=hotspot['net_add'],
        name=hotspot['name'],
        model=hotspot['model'],
      ))
      db.session.commit()


def seed_all():
  seed_users()
  seed_hosts()
  seed_hotspots()
