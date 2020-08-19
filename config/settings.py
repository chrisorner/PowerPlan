from datetime import timedelta
from distutils.util import strtobool
import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
SECRET_KEY = os.getenv('SECRET_KEY', None)

SERVER_NAME = os.getenv('SERVER_NAME',
                        f"localhost:{os.getenv('DOCKER_WEB_PORT','8000')}")

# Flask-Mail.
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = os.getenv('MAIL_PORT', 587)
MAIL_USE_TLS = bool(strtobool(os.getenv('MAIL_USE_TLS', 'true')))
MAIL_USE_SSL = bool(strtobool(os.getenv('MAIL_USE_SSL', 'false')))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', None)
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', None)
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'smtp.gmail.com')

# Celery.
CELERY_BROKER_URL = 'redis://:devpassword@redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:devpassword@redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIS_MAX_CONNECTIONS = 5 

# SQLAlchemy.
db_uri = 'postgresql://energyapp:devpassword@postgres:5432/energyapp'
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

# User.
SEED_NEWSLETTER_EMAIL = 'dev@local.host'
SEED_ADMIN_EMAIL = 'dev@local.host'
SEED_ADMIN_PASSWORD = 'devpassword'
REMEMBER_COOKIE_DURATION = timedelta(days=90)