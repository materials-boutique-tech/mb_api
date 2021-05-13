import os

class DefaultConfig(object):
  DEBUG = False
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("s://", "sql://", 1)
  SECRET_KEY = os.environ.get('SECRET_KEY')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SESSION_COOKIE_SAMESITE = 'None'
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_HTTPONLY = True

class ProductionConfig(DefaultConfig):
  DEBUG = False


class DevelopmentConfig(DefaultConfig):
  DEVELOPMENT = True
  DEBUG = True
