from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager


debug_toolbar = DebugToolbarExtension()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()