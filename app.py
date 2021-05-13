from controllers.auth import auth
from controllers.main import main
from controllers.host import host
from controllers.hotspot import hotspot
from controllers.invoice import invoice
from utils.helium_api_utils import generate_invoices_job
from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager
from models.User import User
from flask_cors import CORS
from db import db
import os
from utils.request_utils import not_authorized_401
from seed.seed import seed_all
from flask_apscheduler import APScheduler
from utils.logging_utils import init_logger, info_log

def create_app():
  load_dotenv()
  login_manager = LoginManager()
  _app = Flask(__name__)
  config = os.environ['APP_SETTINGS']
  _app.config.from_object(config)
  login_manager.init_app(_app)
  CORS(_app, supports_credentials=True, origins=os.environ['CORS_ORIGINS'])
  init_logger(_app)
  info_log("starting app with config: {}".format(config))

  # set up the scheduler for running the invoice generation job
  scheduler = APScheduler()
  scheduler.api_enabled = True
  scheduler.init_app(_app)
  scheduler.start()
  scheduler.add_job(id='invoice_task_id',
                    func=generate_invoices_job(_app),
                    trigger='interval',
                    seconds=10) # TODO: change this to something less frequent

  # set up the user loader for flask_login
  @login_manager.user_loader
  def load_user(user_id):
    return User.query.get(user_id)

  return _app


app = create_app()

app.register_blueprint(main, url_prefix='/')
app.register_blueprint(host, url_prefix='/hosts')
app.register_blueprint(hotspot, url_prefix='/hotspots')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(invoice, url_prefix='/invoices')
app.register_error_handler(401, not_authorized_401)

with app.app_context():
  db.init_app(app)
  db.drop_all()
  db.create_all()
  seed_all()

if __name__ == '__main__':
  app.run(port=5000)
