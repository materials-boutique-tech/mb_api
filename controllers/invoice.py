from flask import Blueprint, Response, jsonify, request
from flask_login import login_required

from db import db
from models.HostInvoice import HostInvoice
from utils.invoice_utils import generate_invoices
from utils.request_utils import Serializer

invoice = Blueprint('invoice', __name__)


@invoice.route('/', methods=['GET'])
@login_required
def index():
  invoices = HostInvoice.query.all()
  return jsonify(Serializer.serialize_list(invoices))


@invoice.route('/host-invoice', methods=['GET'])
@login_required
def show():
  return HostInvoice.by_id(request.args.get('host_invoice_id')).serialize()


@invoice.route('/host-invoices-by-host', methods=['GET'])
@login_required
def by_host():
  host_invoices_for_host = HostInvoice.by_host(request.args.get('host_id'))
  return jsonify(Serializer.serialize_list(host_invoices_for_host))


@invoice.route('/generate', methods=['GET'])
@login_required
def create_invoices():
  generate_invoices()
  return Response('invoices created', status=201, mimetype='application/json')


@invoice.route('/delete-all', methods=['GET'])
@login_required
def delete_all():
  HostInvoice.query.delete()
  db.session.commit()
  return Response('invoices deleted', status=201, mimetype='application/json')
