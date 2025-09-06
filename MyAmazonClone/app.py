from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# Define the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Define and create the instance folder path
instance_path = os.path.join(basedir, 'instance')
app.instance_path = instance_path
os.makedirs(app.instance_path, exist_ok=True)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'store.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


# Import models here to avoid circular import issues and make them known to the CLI
from .models import User

@app.cli.command('init-db')
def init_db_command():
    """Creates the database tables."""
    db.create_all()
    print('Initialized the database.')
