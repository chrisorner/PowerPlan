DEBUG = True

SERVER_NAME = 'localhost:8000'
SECRET_KEY = 'insecurekeyfordev'

# SQLAlchemy.
db_uri = 'postgresql://energyapp:devpassword@postgres:5432/energyapp'
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

# User.
SEED_ADMIN_EMAIL = 'dev@local.host'