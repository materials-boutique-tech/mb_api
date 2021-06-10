from flask import Blueprint, request, jsonify, Response
from flask_login import login_required

from models.Assignment import Assignment

assignment = Blueprint('assignment', __name__)


@assignment.route('/', methods=['GET'])
@login_required
def index():
  assignments = Assignment.all_assignments()

  return jsonify([
    {
      'assignment_id': str(a.assignment_id),
      'host_name': "{} {}".format(a.first_name, a.last_name),
      'host_id': str(a.host_id),
      'hotspot_id': str(a.hotspot_id),
      'hotspot_name': a.name,
      'start_date': a.start_date,
      'end_date': a.end_date,
      'mb_termination_aggressor': a.mb_termination_aggressor,
      'supplement_received': a.supplement_received,
      'host_reward_percentage': a.host_reward_percentage,
      'referer_reward_percentage': a.referer_reward_percentage,
    }
    for a in assignments])


@assignment.route('/assignment', methods=['GET'])
@login_required
def get_assignment():
  return Assignment.by_id(request.args.get('assignment_id'))


@assignment.route('/add', methods=['POST'])
@login_required
def add_assignment():
  Assignment.add(request.json)
  return Response('assignment created', status=201, mimetype='application/json')


@assignment.route('/update', methods=['POST'])
@login_required
def update_assignment():
  Assignment.update(request.json)
  return Response('assignment updated', status=200, mimetype='application/json')
