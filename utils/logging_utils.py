import logging
import sys
logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger('Flask.foo')

def init_logger(_app):
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
  _app.logger.addHandler(handler)
  _app.logger.setLevel(logging.DEBUG)

def info_log(msg):
  log.info(msg)
