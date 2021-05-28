from flask import Blueprint, Response, request, jsonify
from flask_login import current_user
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from models.User import User
from utils.request_utils import Serializer

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login():
  email = request.json['email']
  password = request.json['password']

  user = User.query.filter_by(email=email).first()

  if not user or not check_password_hash(user.password, password):
    return Response('bad credentials', status=401, mimetype='application/json')

  login_user(user, remember=False)
  return Response('login success', status=200, mimetype='application/json')


@auth.route('/signup', methods=['POST'])
@login_required
def signup():
  email = request.json['email']
  user = User.query.filter_by(email=email).first()

  if user:
    return Response('email already in use', status=201, mimetype='application/json')

  first_name = request.json['first_name']
  last_name = request.json['last_name']
  password = request.json['password']

  # noinspection PyArgumentList
  new_user = User(email=email, first_name=first_name, last_name=last_name,
                  password=generate_password_hash(password, method='sha256'))

  db.session.add(new_user)
  db.session.commit()
  return Response('user created', status=201, mimetype='application/json')


@auth.route('/logout')
@login_required
def logout():
  logout_user()
  return Response('logged out', status=200, mimetype='application/json')


@auth.route('/users')
@login_required
def index():
  _users = User.query.all()
  return jsonify(Serializer.serialize_list(_users))


@auth.route('/check-login')
def check_login():
  if current_user.is_authenticated:
    return Response('authenticated', status=200, mimetype='application/json')
  else:
    return Response('not_authenticated', status=200, mimetype='application/json')
