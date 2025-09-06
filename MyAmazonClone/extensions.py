from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions here to avoid circular imports
db = SQLAlchemy()
login_manager = LoginManager()
