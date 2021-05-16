from flask import Blueprint, Response, jsonify
from flask_login import login_required

from db import db
from models.Invoice import Invoice
from utils.helium_api_utils import generate_invoices
from utils.request_utils import Serializer

invoice = Blueprint('invoice', __name__)


@invoice.route('/', methods=['GET'])
@login_required
def index():
  invoices = Invoice.query.all()
  return jsonify(Serializer.serialize_list(invoices))


@invoice.route('/generate', methods=['GET'])
@login_required
def create_invoices():
  generate_invoices()
  return Response('invoices created', status=201, mimetype='application/json')


@invoice.route('/delete-all', methods=['GET'])
@login_required
def delete_all():
  Invoice.query.delete()
  db.session.commit()
  return Response('invoices deleted', status=201, mimetype='application/json')
