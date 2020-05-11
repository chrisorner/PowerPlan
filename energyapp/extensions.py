from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect


debug_toolbar = DebugToolbarExtension()
db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()